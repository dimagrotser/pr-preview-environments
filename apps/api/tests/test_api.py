import os

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_reports_ok():
    res = client.get("/api/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_items_are_returned():
    res = client.get("/api/items")
    assert res.status_code == 200
    assert len(res.json()["items"]) > 0


def test_version_reflects_the_build_environment():
    res = client.get("/api/version")
    assert res.status_code == 200
    body = res.json()
    assert body["pr"] == os.environ.get("PR_NUMBER", "local")
    assert body["commit"] == os.environ.get("GIT_SHA", "dev")


def test_unknown_routes_are_404():
    assert client.get("/api/nope").status_code == 404
