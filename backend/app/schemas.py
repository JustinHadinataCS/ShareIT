from datetime import datetime

from fastapi import UploadFile
from pydantic import BaseModel, Field, field_validator

MIN_EXPIRY_SECONDS = 5 * 60
MAX_EXPIRY_SECONDS = 7 * 24 * 60 * 60


class UploadForm(BaseModel):
    file: UploadFile
    expires_in: int = Field(ge=MIN_EXPIRY_SECONDS, le=MAX_EXPIRY_SECONDS)
    max_downloads: int = Field(ge=1, le=50)
    password: str | None = Field(default=None, max_length=128)

    @field_validator("password")
    @classmethod
    def empty_password_means_none(cls, value: str | None) -> str | None:
        return value or None


class UploadResponse(BaseModel):
    share_id: str
    share_url: str
    expires_at: datetime
