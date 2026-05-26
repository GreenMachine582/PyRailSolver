from fastapi.testclient import TestClient

from app.main import app


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_lifespan_runs() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
