import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.models.database import init_db
from app.routers.message import router as message_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ppurio")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("서버 시작 완료")
    yield
    logger.info("서버 종료")


app = FastAPI(
    title="Y-Union Ppurio Send API",
    description="노동조합 가입 환영 카카오톡 알림톡 발송 API",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(message_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
