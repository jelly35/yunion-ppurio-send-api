from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Google Apps Script 인증
    google_app_script_api_key: str

    # 뿌리오 API
    ppurio_api_key: str
    ppurio_account: str
    sender_profile: str

    # Slack
    slack_webhook_url: str = ""

    # 서버
    server_port: int = 5000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
