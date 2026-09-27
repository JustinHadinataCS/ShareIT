import time

import pytest

from app.schemas import MAX_EXPIRY_SECONDS, MIN_EXPIRY_SECONDS
from app.security import password_hasher


def get_share(aws, share_id):
    return aws.table.get_item(Key={"share_id": share_id})["Item"]


def test_upload_stores_file_and_share(upload, aws):
    started = int(time.time())
    response = upload()

    assert response.status_code == 201
    share_id = response.json()["share_id"]
    assert response.json()["share_url"] == f"http://testserver/share/{share_id}"

    share = get_share(aws, share_id)
    assert share["filename"] == "notes.txt"
    assert share["size"] == 5
    assert share["downloads_remaining"] == 3
    assert started + 3600 <= share["expires_at"] <= int(time.time()) + 3600
    assert "password_hash" not in share

    stored = aws.s3.get_object(Bucket=aws.bucket, Key=share["s3_key"])
    assert stored["Body"].read() == b"hello"


def test_password_is_stored_as_argon2_hash(upload, aws):
    share = get_share(aws, upload(password="secret").json()["share_id"])

    assert share["password_hash"] != "secret"
    assert password_hasher.verify(share["password_hash"], "secret")


def test_empty_password_means_no_password(upload, aws):
    share = get_share(aws, upload(password="").json()["share_id"])

    assert "password_hash" not in share


@pytest.mark.parametrize(
    "fields",
    [
        {"expires_in": MIN_EXPIRY_SECONDS - 1},
        {"expires_in": MAX_EXPIRY_SECONDS + 1},
        {"max_downloads": 0},
        {"max_downloads": 51},
        {"password": "x" * 129},
    ],
)
def test_rejects_out_of_range_options(upload, fields):
    assert upload(**fields).status_code == 422


def test_rejects_missing_file(client):
    response = client.post("/api/files", data={"expires_in": 3600, "max_downloads": 3})

    assert response.status_code == 422


def test_rejects_empty_file(upload):
    assert upload(content=b"").status_code == 400


def test_rejects_file_over_10_mb_without_storing_it(upload, aws):
    response = upload(content=b"x" * (10 * 1024 * 1024 + 1))

    assert response.status_code == 413
    assert aws.s3.list_objects_v2(Bucket=aws.bucket)["KeyCount"] == 0


def test_keeps_only_the_base_filename(upload, aws):
    share = get_share(aws, upload(filename="../../etc/passwd").json()["share_id"])

    assert share["filename"] == "passwd"
