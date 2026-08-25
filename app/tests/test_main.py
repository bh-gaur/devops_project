import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to the Zero-Trust DevOps Platform API"
    assert "version" in data


def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data
    assert "version" in data


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "app_requests_total" in response.text


def test_simulate_error():
    response = client.get("/simulate/error")
    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Synthetic failure triggered for rollback testing."


def test_simulate_latency():
    response = client.get("/simulate/latency?seconds=0.1")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "delayed"
    assert data["latency_seconds"] == 0.1
