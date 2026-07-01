from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./codeleaderboard.db"
    redis_url: str = "redis://localhost:6379/0"
    api_tokens: List[str] = ["dev-token-123"]
    max_concurrent_evaluations: int = 3
    task_timeout_seconds: int = 1800
    datasets_config_path: str = "./datasets"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
