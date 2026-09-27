from datetime import datetime

from pydantic import BaseModel, Field

MIN_EXPIRY_SECONDS = 5 * 60
MAX_EXPIRY_SECONDS = 7 * 24 * 60 * 60
MAX_PASSWORD_LENGTH = 128


class UploadResponse(BaseModel):
    share_id: str
    share_url: str
    expires_at: datetime


class ShareInfo(BaseModel):
    filename: str
    size: int
    expires_at: datetime
    password_required: bool


class DownloadRequest(BaseModel):
    password: str | None = Field(default=None, max_length=MAX_PASSWORD_LENGTH)


class DownloadResponse(BaseModel):
    url: str
