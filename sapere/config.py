import os
from pathlib import Path

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

_project_root = Path(__file__).parent.parent
_env_path = _project_root / ".env"
load_dotenv(_env_path, override=True)


class AppConfig(BaseSettings):
    model_config = {"extra": "ignore"}

    db_path: str = "data/sapere.db"
    debug: bool = False

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = "gemini-3-flash-preview"
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    request_timeout: int = 60
    max_retries: int = 3
    max_tokens: int = 16384

    pomodoro_duration_min: int = 50
    short_break_min: int = 10
    long_break_min: int = 15
    blocks_before_long_break: int = 3
    max_blocks_per_day: int = 4


config = AppConfig()
