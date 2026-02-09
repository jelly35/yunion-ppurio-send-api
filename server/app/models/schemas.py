from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    phoneNumber: str = Field(..., description="수신자 전화번호 (하이픈 없이)", examples=["01012345678"])
    name: str = Field(..., description="수신자 이름", examples=["홍길동"])
    templateId: str = Field(..., description="뿌리오 알림톡 템플릿 코드", examples=["ppur_2026012921485212712316904"])


class SendMessageResponse(BaseModel):
    success: bool
    message: str
    ppurio_response: dict | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: str | None = None
