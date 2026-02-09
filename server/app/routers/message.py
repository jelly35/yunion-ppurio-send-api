import json
import logging

from fastapi import APIRouter, Depends

from app.dependencies import verify_api_key
from app.models.schemas import SendMessageRequest, SendMessageResponse, ErrorResponse
from app.models.database import save_message_log
from app.services.ppurio import ppurio_service, PpurioTokenError
from app.services.slack import send_slack_notification

logger = logging.getLogger("ppurio.router")

router = APIRouter()


@router.post(
    "/send_message",
    response_model=SendMessageResponse,
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="카카오톡 알림톡 발송",
    description="Google Form 가입 신청 시 환영 카카오톡 알림톡을 발송합니다.",
)
async def send_message(
    req: SendMessageRequest,
    _api_key: str = Depends(verify_api_key),
):
    try:
        result = await ppurio_service.send_kakao(
            phone_number=req.phoneNumber,
            name=req.name,
            template_id=req.templateId,
        )

        ppurio_body = result["body"]
        ppurio_code = ppurio_body.get("code", "")
        ppurio_message_key = ppurio_body.get("messageKey", "")
        is_success = result["status_code"] == 200 and ppurio_code == "1000"

        await save_message_log(
            phone=req.phoneNumber,
            name=req.name,
            template_id=req.templateId,
            status="success" if is_success else "failed",
            ref_key=result["ref_key"],
            ppurio_code=ppurio_code,
            ppurio_message_key=ppurio_message_key,
            ppurio_response=json.dumps(ppurio_body, ensure_ascii=False),
        )

        await send_slack_notification(
            is_success=is_success,
            name=req.name,
            phone_number=req.phoneNumber,
            response_code=result["status_code"],
            error=None if is_success else json.dumps(ppurio_body, ensure_ascii=False),
        )

        if is_success:
            return SendMessageResponse(
                success=True,
                message="카카오톡 알림톡 발송 성공",
                ppurio_response=ppurio_body,
            )
        else:
            return SendMessageResponse(
                success=False,
                message="카카오톡 알림톡 발송 실패",
                ppurio_response=ppurio_body,
            )

    except PpurioTokenError as e:
        logger.error("뿌리오 토큰 오류: %s", e)

        await save_message_log(
            phone=req.phoneNumber,
            name=req.name,
            template_id=req.templateId,
            status="token_error",
            ppurio_response=e.detail,
        )

        await send_slack_notification(
            is_success=False,
            name=req.name,
            phone_number=req.phoneNumber,
            response_code=e.status_code,
            error=f"토큰 발급 실패: {e.detail}",
        )

        return SendMessageResponse(
            success=False,
            message="뿌리오 토큰 발급 실패",
            ppurio_response={"error": e.detail},
        )

    except Exception as e:
        logger.exception("메시지 발송 중 예외 발생")

        await save_message_log(
            phone=req.phoneNumber,
            name=req.name,
            template_id=req.templateId,
            status="error",
            ppurio_response=str(e),
        )

        await send_slack_notification(
            is_success=False,
            name=req.name,
            phone_number=req.phoneNumber,
            error=str(e),
        )

        return SendMessageResponse(
            success=False,
            message="서버 내부 오류",
        )
