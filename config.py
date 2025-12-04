from pydantic import BaseSettings
from functools import cache


class Settings(BaseSettings):
    # Temporal
    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"
    task_queue: str = "lab-workflow-task-queue"

    class Config:
        env_file = ".env"


@cache
def get_settings() -> Settings:
    return Settings()
