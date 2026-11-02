from fastapi.testclient import TestClient
from app.core.config import settings
from app.main import app

client = TestClient(app)

def test_metrics_requires_api_key():
    response = client.get("/metrics")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_metrics_with_valid_api_key():
    headers = {"X-API-Key": settings.api_key}
    response = client.get("/metrics", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"metrics": "some metrics data"}