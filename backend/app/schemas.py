from datetime import datetime

from pydantic import BaseModel

MIN_EXPIRY_SECONDS = 5 * 60
MAX_EXPIRY_SECONDS = 7 * 24 * 60 * 60


class UploadResponse(BaseModel):
    share_id: str
    share_url: str
    expires_at: datetime
