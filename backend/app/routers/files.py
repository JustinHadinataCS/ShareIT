import os
import time
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status

from app.aws import get_s3_client, get_table
from app.config import Settings, get_settings
from app.schemas import MAX_EXPIRY_SECONDS, MIN_EXPIRY_SECONDS, UploadResponse
from app.security import generate_share_id, hash_password

router = APIRouter(prefix="/api")


# A plain `def` (not async) so FastAPI runs the blocking boto3 calls in a thread pool.
@router.post("/files", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def upload_file(
    file: UploadFile,
    expires_in: Annotated[int, Form(ge=MIN_EXPIRY_SECONDS, le=MAX_EXPIRY_SECONDS)],
    max_downloads: Annotated[int, Form(ge=1, le=50)],
    settings: Annotated[Settings, Depends(get_settings)],
    password: Annotated[str | None, Form(max_length=128)] = None,
    s3=Depends(get_s3_client),
    table=Depends(get_table),
):
    if not file.size:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File is empty")
    if file.size > settings.max_file_size:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "File is larger than 10 MB")

    filename = os.path.basename(file.filename or "") or "file"
    share_id = generate_share_id()
    s3_key = share_id
    expires_at = int(time.time()) + expires_in

    s3.upload_fileobj(
        file.file,
        settings.s3_bucket,
        s3_key,
        ExtraArgs={"ContentType": file.content_type or "application/octet-stream"},
    )

    item = {
        "share_id": share_id,
        "filename": filename,
        "s3_key": s3_key,
        "size": file.size,
        "expires_at": expires_at,
        "downloads_remaining": max_downloads,
    }
    if password:
        item["password_hash"] = hash_password(password)

    table.put_item(Item=item, ConditionExpression="attribute_not_exists(share_id)")

    return UploadResponse(
        share_id=share_id,
        share_url=f"{settings.public_url}/share/{share_id}",
        expires_at=datetime.fromtimestamp(expires_at, tz=timezone.utc),
    )
