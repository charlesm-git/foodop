from fastapi.testclient import TestClient

from config import __version__
from main import app


def test_health():
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "version": __version__}
