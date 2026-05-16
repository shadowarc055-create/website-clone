from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql+asyncpg://osint:osint@localhost:5432/osint"
    repository_backend: str = "memory"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "osint-password"
    opensearch_url: str = "http://localhost:9200"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    enable_dark_web: bool = False
    breach_index_path: str | None = None
    dark_web_index_path: str | None = None
    queue_mode: str = "inline"
    max_recursion_depth: int = 3
    min_confidence_to_pivot: float = 0.35

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
