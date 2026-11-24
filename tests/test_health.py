from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "sift"}


def test_frontend_shell_is_served() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Don't just read it." in response.text
    assert "/app.js" in response.text
    assert 'id="url-inspections"' in response.text
