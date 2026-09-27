import time
from urllib.parse import parse_qs, urlparse

import requests

from app.routers import shares


def create_share(upload, **fields):
    return upload(**fields).json()["share_id"]


def test_share_info_shows_only_public_details(client, upload):
    share_id = create_share(upload, filename="report.pdf")

    response = client.get(f"/api/share/{share_id}")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"filename", "size", "expires_at", "password_required"}
    assert body["filename"] == "report.pdf"
    assert body["size"] == 5
    assert body["password_required"] is False


def test_share_info_says_when_a_password_is_needed(client, upload):
    share_id = create_share(upload, password="secret")

    assert client.get(f"/api/share/{share_id}").json()["password_required"] is True


def test_unknown_link_is_404(client):
    assert client.get("/api/share/nope").status_code == 404
    assert client.post("/api/share/nope/download").status_code == 404


def test_expired_link_is_410_even_before_ttl_deletes_it(client, upload, aws):
    share_id = create_share(upload)
    aws.table.update_item(
        Key={"share_id": share_id},
        UpdateExpression="SET expires_at = :past",
        ExpressionAttributeValues={":past": int(time.time()) - 1},
    )

    assert client.get(f"/api/share/{share_id}").status_code == 410
    assert client.post(f"/api/share/{share_id}/download").status_code == 410


def test_download_returns_a_short_lived_url_to_the_file(client, upload):
    share_id = create_share(upload, filename="notes.txt")

    response = client.post(f"/api/share/{share_id}/download")

    assert response.status_code == 200
    url = response.json()["url"]
    query = parse_qs(urlparse(url).query)
    assert query["X-Amz-Expires"] == ["60"]
    assert query["response-content-disposition"][0].startswith('attachment; filename="notes.txt"')
    assert requests.get(url).content == b"hello"


def test_download_limit(client, upload):
    share_id = create_share(upload, max_downloads=1)
    download = f"/api/share/{share_id}/download"

    assert client.post(download).status_code == 200
    assert client.post(download).status_code == 410
    assert client.get(f"/api/share/{share_id}").status_code == 410


def test_last_download_cannot_be_used_twice_in_a_race(client, upload, aws, monkeypatch):
    share_id = create_share(upload, max_downloads=1)
    # What a second request read just before the first one used the last download.
    stale_share = aws.table.get_item(Key={"share_id": share_id})["Item"]
    download = f"/api/share/{share_id}/download"

    assert client.post(download).status_code == 200
    monkeypatch.setattr(shares, "get_active_share", lambda table, share_id: stale_share)
    assert client.post(download).status_code == 410


def test_password_is_checked_before_a_download_is_used(client, upload):
    share_id = create_share(upload, max_downloads=1, password="secret")
    download = f"/api/share/{share_id}/download"

    assert client.post(download).status_code == 401
    assert client.post(download, json={"password": "wrong"}).status_code == 401
    assert client.post(download, json={"password": "secret"}).status_code == 200
