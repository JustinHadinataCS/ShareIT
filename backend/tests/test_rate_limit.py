from fastapi.testclient import TestClient

from app.main import app


def assert_rate_limited(response):
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    assert "Too many requests" in response.json()["detail"]


def test_uploads_are_limited_to_10_a_minute(upload):
    for _ in range(10):
        assert upload().status_code == 201

    assert_rate_limited(upload())


def test_share_info_is_limited_to_60_a_minute(client, upload):
    share_id = upload().json()["share_id"]
    for _ in range(60):
        assert client.get(f"/api/share/{share_id}").status_code == 200

    assert_rate_limited(client.get(f"/api/share/{share_id}"))


def test_password_guessing_is_limited_to_10_a_minute(client, upload):
    share_id = upload(max_downloads=50, password="secret").json()["share_id"]
    download = f"/api/share/{share_id}/download"
    for _ in range(10):
        assert client.post(download, json={"password": "wrong"}).status_code == 401

    # Blocked even with the right password until the minute is up.
    assert_rate_limited(client.post(download, json={"password": "secret"}))


def test_limits_are_per_client(upload):
    for _ in range(10):
        upload()
    assert_rate_limited(upload())

    someone_else = TestClient(app, client=("203.0.113.7", 50000))
    response = someone_else.post(
        "/api/files",
        data={"expires_in": 3600, "max_downloads": 1},
        files={"file": ("a.txt", b"hi", "text/plain")},
    )
    assert response.status_code == 201
