# 기존 Dockerfile에 추가
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# logs 디렉토리 생성 및 권한 설정
RUN mkdir -p /app/logs

# 애플리케이션 실행
CMD ["python", "ppurio_send_kakaotalk.py"]

