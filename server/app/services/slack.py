import logging

import httpx

from app.config import settings

logger = logging.getLogger("ppurio.slack")


async def send_slack_notification(
    is_success: bool,
    name: str,
    phone_number: str,
    response_code: int | None = None,
    error: str | None = None,
):
    """Slack 웹훅으로 발송 결과 알림"""
    if not settings.slack_webhook_url:
        logger.warning("SLACK_WEBHOOK_URL이 설정되지 않아 알림을 건너뜁니다")
        return

    status_emoji = "✅" if is_success else "❌"
    status_text = "성공" if is_success else "실패"

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{status_emoji} *카카오톡 메시지 발송 {status_text}*",
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*이름:*\n{name}"},
                {"type": "mrkdwn", "text": f"*휴대전화번호:*\n{phone_number}"},
            ],
        },
    ]

    if not is_success:
        if response_code is not None:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*HTTP 상태 코드:*\n{response_code}"},
            })
        if error:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*오류 메시지:*\n{error}"},
            })

    blocks.append({
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": "이 메시지는 Y-Union Ppurio API 서버에서 자동으로 생성되었습니다."},
        ],
    })

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                settings.slack_webhook_url,
                json={"blocks": blocks},
            )
            if resp.status_code == 200:
                logger.info("Slack 알림 발송 성공")
            else:
                logger.warning("Slack 알림 발송 실패: status=%d", resp.status_code)
    except Exception:
        logger.exception("Slack 알림 발송 중 오류 발생")
