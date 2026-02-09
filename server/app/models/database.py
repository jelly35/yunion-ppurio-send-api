import aiosqlite
import logging
import os

logger = logging.getLogger("ppurio.database")

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "messages.db")


async def init_db():
    """SQLite 데이터베이스 초기화 및 테이블 생성"""
    os.makedirs(DB_DIR, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone VARCHAR(20) NOT NULL,
                name VARCHAR(100) NOT NULL,
                template_id VARCHAR(100),
                status VARCHAR(20) NOT NULL,
                ref_key VARCHAR(50),
                ppurio_code VARCHAR(10),
                ppurio_message_key VARCHAR(100),
                ppurio_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    logger.info("데이터베이스 초기화 완료: %s", DB_PATH)


async def save_message_log(
    phone: str,
    name: str,
    template_id: str,
    status: str,
    ref_key: str = "",
    ppurio_code: str = "",
    ppurio_message_key: str = "",
    ppurio_response: str = "",
):
    """발송 이력 저장"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO message_logs
                (phone, name, template_id, status, ref_key, ppurio_code, ppurio_message_key, ppurio_response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (phone, name, template_id, status, ref_key, ppurio_code, ppurio_message_key, ppurio_response),
        )
        await db.commit()
    logger.info("발송 이력 저장: name=%s, status=%s", name, status)
