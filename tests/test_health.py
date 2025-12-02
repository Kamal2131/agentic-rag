import pytest


@pytest.mark.django_db
class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_endpoint_success(self, api_client):
        """Test health endpoint returns 200."""
        response = api_client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "agentic-rag"
        assert "database" in data

    def test_readiness_endpoint(self, api_client):
        """Test readiness endpoint."""
        response = api_client.get("/ready/")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "ready" in data
        assert "checks" in data
