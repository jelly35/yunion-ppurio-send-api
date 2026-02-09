# Y-Union Ppurio Send API

노동조합 Google Form 가입 신청 시 카카오톡 알림톡 환영 메시지를 자동 발송하는 시스템입니다.

## 시스템 구성

```
Google Form 제출
      ↓
Google Apps Script (appscript.gs)
      ↓ POST /send_message (x-api-key 인증)
FastAPI 서버 (Docker)
      ↓
뿌리오 API → 카카오톡 알림톡 발송
      ↓
Slack 알림 (성공/실패)
SQLite 발송 이력 저장
```

## 프로젝트 구조

```
yunion-ppurio-send-api/
├── .env                    # 환경변수 (시크릿, .gitignore 대상)
├── .env.example            # 환경변수 템플릿
├── docker-compose.yml
├── appscript/
│   └── appscript.gs        # Google Apps Script
├── server/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # FastAPI 앱 진입점
│       ├── config.py        # 환경변수 설정
│       ├── dependencies.py  # API 키 인증
│       ├── routers/
│       │   └── message.py   # /send_message 엔드포인트
│       ├── services/
│       │   ├── ppurio.py    # 뿌리오 API 클라이언트 (토큰 캐싱)
│       │   └── slack.py     # Slack 알림
│       └── models/
│           ├── schemas.py   # Pydantic 스키마
│           └── database.py  # SQLite 발송 이력
└── docs/
    └── ppurio_api_guide.md  # 뿌리오 API 가이드
```

## 빠른 시작

### 1. 환경변수 설정

```bash
cp .env.example .env
# .env 파일에 실제 시크릿 값 입력
```

### 2. Docker로 실행

```bash
docker compose up -d --build
```

### 3. 서버 확인

```bash
# 헬스체크
curl http://localhost:7936/health

# API 문서 (Swagger UI)
# 브라우저에서 http://localhost:7936/docs 접속
```

### 4. 테스트 발송

```bash
curl -X POST http://localhost:7936/send_message \
  -H "Content-Type: application/json" \
  -H "x-api-key: {YOUR_API_KEY}" \
  -d '{"phoneNumber": "01012345678", "name": "테스트", "templateId": "ppur_2026012921485212712316904"}'
```

## 주요 기능

- **카카오톡 알림톡 자동 발송**: Google Form 가입 → 알림톡 발송
- **토큰 캐싱**: 뿌리오 토큰을 메모리 캐싱하여 불필요한 재발급 방지
- **발송 이력 저장**: SQLite DB에 모든 발송 기록 저장
- **Slack 알림**: 발송 성공/실패 실시간 알림
- **API 문서 자동 생성**: FastAPI Swagger UI (`/docs`)

## Google Apps Script 설정

1. Google Forms 에디터에서 **확장 프로그램 > Apps Script** 열기
2. `appscript/appscript.gs` 내용 붙여넣기
3. CONFIG 객체의 값을 환경에 맞게 수정
4. **트리거 > 트리거 추가** → `onFormSubmit` 함수 등록

## HTTPS 적용 (Caddy 리버스 프록시)

### Caddy 설치 (Oracle Linux / CentOS)

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://yum.caddyserver.com/caddy.repo
sudo yum install -y caddy
```

### Caddyfile 설정

```
ppurio.y-union.org {
    reverse_proxy localhost:7936
}
```

```bash
sudo systemctl enable caddy
sudo systemctl start caddy
```

Caddy가 자동으로 Let's Encrypt SSL 인증서를 발급하고 갱신합니다.
HTTPS 적용 후 Google Apps Script의 `CONFIG.API_URL`을 `https://ppurio.y-union.org/send_message`로 변경하세요.

## 환경변수

| 변수명 | 설명 |
|--------|------|
| `GOOGLE_APP_SCRIPT_API_KEY` | GAS → 서버 인증용 API 키 |
| `PPURIO_API_KEY` | 뿌리오 연동 개발 인증키 |
| `PPURIO_ACCOUNT` | 뿌리오 계정 |
| `SENDER_PROFILE` | 카카오톡 발신 프로필명 |
| `SLACK_WEBHOOK_URL` | Slack 알림 웹훅 URL |
| `SERVER_PORT` | 외부 포트 (기본: 7936) |
