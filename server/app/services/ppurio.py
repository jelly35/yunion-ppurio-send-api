import base64
import logging
import random
import string
import time

import httpx

from app.config import settings

logger = logging.getLogger("ppurio.ppurio_service")

PPURIO_BASE_URL = "https://message.ppurio.com"


class PpurioService:
    """뿌리오 API 클라이언트 (토큰 캐싱 포함)"""

    def __init__(self):
        self._token: str | None = None
        self._token_expires_at: float = 0

    def _is_token_valid(self) -> bool:
        # 만료 1시간 전에 갱신
        return self._token is not None and time.time() < (self._token_expires_at - 3600)

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        if self._is_token_valid():
            return self._token

        auth_str = f"{settings.ppurio_account}:{settings.ppurio_api_key}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode("utf-8")

        response = await client.post(
            f"{PPURIO_BASE_URL}/v1/token",
            headers={"Authorization": f"Basic {encoded_auth}"},
        )

        if response.status_code != 200:
            logger.error("토큰 발급 실패: %s", response.text)
            raise PpurioTokenError(response.status_code, response.text)

        data = response.json()
        self._token = data["token"]
        # 뿌리오 토큰 만료: epoch ms → seconds
        self._token_expires_at = data.get("expired", 0) / 1000
        logger.info("뿌리오 토큰 발급 성공 (만료: %s)", self._token_expires_at)
        return self._token

    async def send_kakao(
        self,
        phone_number: str,
        name: str,
        template_id: str,
    ) -> dict:
        """카카오톡 알림톡 발송"""
        async with httpx.AsyncClient(timeout=30) as client:
            token = await self._get_token(client)

            ref_key = "".join(random.choices(string.ascii_letters + string.digits, k=32))

            payload = {
                "account": settings.ppurio_account,
                "messageType": "ALT",
                "senderProfile": settings.sender_profile,
                "templateCode": template_id,
                "duplicateFlag": "N",
                "targetCount": 1,
                "targets": [
                    {
                        "to": phone_number,
                        "name": name,
                        "changeWord": {"var1": f"Welcome, {name}"},
                    }
                ],
                "isResend": "N",
                "resend": {
                    "messageType": "SMS",
                    "from": "01012341234",
                    "content": "카카오톡 발송이 불가하여 SMS로 대체 발송합니다.",
                },
                "refKey": ref_key,
            }

            response = await client.post(
                f"{PPURIO_BASE_URL}/v1/kakao",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            logger.info("카카오톡 발송 응답: status=%d, body=%s", response.status_code, response.text)

            try:
                body = response.json()
            except Exception:
                body = {"raw": response.text}

            return {
                "status_code": response.status_code,
                "body": body,
                "ref_key": ref_key,
            }


class PpurioTokenError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"토큰 발급 실패 (status={status_code}): {detail}")


# 싱글톤 인스턴스
ppurio_service = PpurioService()
