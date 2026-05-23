"""
AlgoMentor AI — CORS tests.

Verifies that the FastAPI application allows cross-origin requests
from the configured frontend origins but blocks other origins.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_cors_preflight_allowed_origin():
    """OPTIONS request from localhost:5173 is allowed."""
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_preflight_allowed_origin_alt():
    """OPTIONS request from 127.0.0.1:5173 is allowed."""
    headers = {
        "Origin": "http://127.0.0.1:5173",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"


def test_cors_preflight_disallowed_origin():
    """OPTIONS request from malicious origin does not get an allowed origin response."""
    headers = {
        "Origin": "http://malicious-example.test",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/health", headers=headers)
    # The preflight response shouldn't include the malicious origin.
    assert "access-control-allow-origin" not in response.headers


def test_cors_get_request_allowed_origin():
    """Actual GET request from allowed origin works and returns CORS headers."""
    headers = {
        "Origin": "http://localhost:5173",
    }
    response = client.get("/health", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
