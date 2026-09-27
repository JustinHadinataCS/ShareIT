from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    aws_region: str
    s3_bucket: str
    dynamodb_table: str
    public_url: str = "http://localhost:5173"
    max_file_size: int = 10 * 1024 * 1024

    @field_validator("public_url")
    @classmethod
    def strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
