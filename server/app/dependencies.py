import logging
from fastapi import Header, HTTPException

from app.config import settings

logger = logging.getLogger("ppurio.auth")


async def verify_api_key(x_api_key: str = Header(..., description="Google Apps Script 인증 API 키")):
    """x-api-key 헤더로 API 키 인증"""
    if x_api_key != settings.google_app_script_api_key:
        logger.warning("인증 실패: 잘못된 API 키")
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_api_key
