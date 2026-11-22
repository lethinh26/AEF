from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AEO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://aeo:aeo_local_only_change_me@127.0.0.1:5432/aeo"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    s3_endpoint_url: str = "http://127.0.0.1:9000"
    s3_access_key: str = "aeo-local"
    s3_secret_key: str = "aeo_local_object_store_change_me"
    s3_bucket: str = "aeo-artifacts"


@lru_cache
def get_settings() -> Settings:
    return Settings()
