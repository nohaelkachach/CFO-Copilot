# tests/test_health.py

def test_health_check(client):
    """Confirms the API is running and reachable."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_reachable(client):
    """Confirms Swagger UI is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200