"""
Unit tests for main.py endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the /health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "message" in data
    assert "timestamp" in data
    assert "version" in data


def test_status_endpoint():
    """Test the /api/status endpoint"""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["backend_status"] == "operational"
    assert "message" in data
    assert "timestamp" in data


def test_info_endpoint():
    """Test the /api/info endpoint"""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "version" in data
    assert "serve_frontend" in data
    assert "environment" in data


def test_cors_headers():
    """Test that CORS headers are present"""
    response = client.options("/health")
    assert response.status_code == 200


def test_docs_available():
    """Test that API docs are available"""
    response = client.get("/docs")
    assert response.status_code == 200
