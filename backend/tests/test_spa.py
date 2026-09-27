import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.spa import SPAStaticFiles


@pytest.fixture
def client(tmp_path):
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("react app")
    (static / "favicon.svg").write_text("icon")
    (tmp_path / "secret.txt").write_text("secret")

    app = FastAPI()
    app.mount("/", SPAStaticFiles(directory=static, html=True))
    return TestClient(app)


def test_serves_built_files(client):
    assert client.get("/favicon.svg").text == "icon"


@pytest.mark.parametrize("path", ["/", "/share/abc123"])
def test_react_routes_get_index_html(client, path):
    response = client.get(path)

    assert response.status_code == 200
    assert response.text == "react app"


def test_unknown_api_paths_stay_404(client):
    assert client.get("/api/nope").status_code == 404


def test_cannot_read_files_outside_static_dir(client):
    assert "secret" not in client.get("/%2e%2e/secret.txt").text
