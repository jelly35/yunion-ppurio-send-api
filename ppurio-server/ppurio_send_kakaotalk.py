from flask import Flask, request, jsonify
import requests
import os
import logging
from logging.handlers import RotatingFileHandler
import base64
import random
import string

app = Flask(__name__)

# 로그 디렉토리 및 파일 설정
if not os.path.exists('logs'):
    os.makedirs('logs')

# Disable default Flask logger configuration
app.logger.propagate = False

# 액세스 로그 설정
access_handler = RotatingFileHandler('logs/access.log', maxBytes=10240, backupCount=10)
access_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(remote_addr)s - %(method)s - %(url)s - %(status_code)s'
))
access_handler.setLevel(logging.INFO)
access_log = logging.getLogger('access_logger')
access_log.addHandler(access_handler)
access_log.setLevel(logging.INFO)

# 에러 로그 설정
error_handler = RotatingFileHandler('logs/error.log', maxBytes=10240, backupCount=10)
error_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
error_handler.setLevel(logging.ERROR)
app.logger.addHandler(error_handler)

# 앱 시작 시 로깅
app.logger.setLevel(logging.INFO)
app.logger.info('Ppurio API Flask app startup')

# 환경 변수에서 API 키를 로드 (API_KEY는 EC2와 Google Apps Script 간의 인증용)
GOOGLE_APP_SCRIPT_API_KEY = os.environ.get('GOOGLE_APP_SCRIPT_API_KEY', 'your_secure_api_key')

# 뿌리오 계정 정보와 API 키를 환경 변수에서 로드
PPURIO_API_KEY = os.environ.get('PPURIO_API_KEY', '{연동 개발 인증키}')
PPURIO_ACCOUNT = os.environ.get('PPURIO_ACCOUNT', '{뿌리오 계정}')
SENDER_PROFILE = os.environ.get('SENDER_PROFILE', '{발신프로필명}')
# TEMPLATE_CODE = os.environ.get('TEMPLATE_CODE', '{뿌리오에 등록된 알림톡 템플릿 코드}')

def validate_api_key(provided_key):
    return provided_key == GOOGLE_APP_SCRIPT_API_KEY

@app.before_request
def log_request_info():
    # 액세스 로그에 요청 정보 기록
    request.access_log_data = {
        'remote_addr': request.remote_addr,
        'method': request.method,
        'url': request.url,
    }

@app.after_request
def log_response_info(response):
    # 액세스 로그에 응답 정보 기록
    request.access_log_data['status_code'] = response.status_code
    access_log.info(
    f"{request.remote_addr} - {request.method} - {request.url} - {response.status_code}"
    )
    return response

@app.route('/send_message', methods=['POST'])
def send_message():
    # Google Apps Script에서 보내는 API 키 인증
    provided_key = request.headers.get('x-api-key')
    if not validate_api_key(provided_key):
        app.logger.warning('Unauthorized access attempt with key: %s', provided_key)
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    phone_number = data['phoneNumber']
    name = data['name']
    template_id = data.get('templateId')

    try:
        # 뿌리오 토큰 요청
        auth_str = f"{PPURIO_ACCOUNT}:{PPURIO_API_KEY}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode('utf-8')
        token_response = requests.post(
            'https://message.ppurio.com/v1/token',
            headers={'Authorization': f'Basic {encoded_auth}'}
        )
        app.logger.info('Ppurio token response: %s', token_response.text)

        if token_response.status_code == 200:
            token = token_response.json().get('token')
            if token:
                # 카카오톡 메시지 발송
                message_response = requests.post(
                    'https://message.ppurio.com/v1/kakao',
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'account': PPURIO_ACCOUNT,
                        'messageType': 'ALT',
                        'senderProfile': SENDER_PROFILE,
                        'templateCode': template_id,
                        'duplicateFlag': 'N',
                        'targetCount': 1,
                        'targets': [
                            {
                                'to': phone_number,
                                'name': name,
                                'changeWord': {
                                    'var1': 'Welcome, ' + name
                                }
                            }
                        ],
                        'isResend': 'N',
                        'resend': {
                            'messageType': 'SMS',
                            'from': '01012341234',
                            'content': 'This is a resend message in case KakaoTalk is not available.'
                        },
                        'refKey': ''.join(random.choices(string.ascii_letters + string.digits, k=32))
                    }
                )
                app.logger.info('Kakao message response: %s', message_response.text)

                # ✅ 핵심: downstream(뿌리오) status code를 그대로 반환
                try:
                    body = message_response.json()
                except Exception:
                    body = {"raw": message_response.text}

                return jsonify(body), message_response.status_code

            else:
                app.logger.error('Failed to retrieve access token')
                return jsonify({"error": "Failed to retrieve access token"}), 500
        else:
            app.logger.error('Failed to retrieve access token, status code: %s', token_response.status_code)
            # ✅ 토큰 요청 실패도 status code를 그대로 반환(원인 파악 용이)
            return jsonify({"error": "Failed to retrieve access token", "ppurio": token_response.text}), token_response.status_code

    except Exception as e:
        app.logger.exception('Error during message sending process')
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

