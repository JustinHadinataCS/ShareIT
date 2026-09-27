import time
from datetime import datetime, timezone
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status

from app.aws import get_s3_client, get_table
from app.config import Settings, get_settings
from app.rate_limit import DOWNLOAD_LIMIT, SHARE_INFO_LIMIT, limiter
from app.schemas import DownloadRequest, DownloadResponse, ShareInfo
from app.security import verify_password

router = APIRouter(prefix="/api/share")

DOWNLOAD_URL_TTL_SECONDS = 60

ShareId = Annotated[str, Path(max_length=64)]


def get_active_share(table, share_id: str) -> dict:
    share = table.get_item(Key={"share_id": share_id}).get("Item")
    if share is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Link not found")
    # DynamoDB TTL can take a while to delete expired items, so check expiry here too.
    if share["expires_at"] <= int(time.time()):
        raise HTTPException(status.HTTP_410_GONE, "This link has expired")
    if share["downloads_remaining"] <= 0:
        raise HTTPException(status.HTTP_410_GONE, "This link has no downloads left")
    return share


def attachment(filename: str) -> str:
    """Content-Disposition that makes the browser save the file under its original name."""
    ascii_name = "".join(c for c in filename if " " <= c <= "~" and c not in '"\\')
    return f"attachment; filename=\"{ascii_name or 'download'}\"; filename*=UTF-8''{quote(filename)}"


@router.get("/{share_id}", response_model=ShareInfo)
@limiter.limit(SHARE_INFO_LIMIT)
def get_share_info(request: Request, share_id: ShareId, table=Depends(get_table)):
    share = get_active_share(table, share_id)
    return ShareInfo(
        filename=share["filename"],
        size=int(share["size"]),
        expires_at=datetime.fromtimestamp(int(share["expires_at"]), tz=timezone.utc),
        password_required="password_hash" in share,
    )


@router.post("/{share_id}/download", response_model=DownloadResponse)
@limiter.limit(DOWNLOAD_LIMIT)
def download_share(
    request: Request,
    share_id: ShareId,
    settings: Annotated[Settings, Depends(get_settings)],
    body: DownloadRequest | None = None,
    s3=Depends(get_s3_client),
    table=Depends(get_table),
):
    share = get_active_share(table, share_id)

    # Check the password before counting the download, so a wrong guess doesn't use one up.
    if "password_hash" in share:
        password = body.password if body else None
        if not password:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "This file needs a password")
        if not verify_password(share["password_hash"], password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong password")

    # Conditional update: if two people race for the last download, only one succeeds.
    try:
        table.update_item(
            Key={"share_id": share_id},
            UpdateExpression="SET downloads_remaining = downloads_remaining - :one",
            ConditionExpression="downloads_remaining > :zero AND expires_at > :now",
            ExpressionAttributeValues={":one": 1, ":zero": 0, ":now": int(time.time())},
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        raise HTTPException(status.HTTP_410_GONE, "This link has no downloads left") from None

    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": share["s3_key"],
            "ResponseContentDisposition": attachment(share["filename"]),
        },
        ExpiresIn=DOWNLOAD_URL_TTL_SECONDS,
    )
    return DownloadResponse(url=url)
