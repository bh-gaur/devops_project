import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.observability import (
    setup_tracing,
    get_tracer,
    REQUEST_COUNT,
    get_metrics_response,
)

app = FastAPI(
    title="Autonomous DevOps Super Platform API",
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Microservice with OpenTelemetry instrumentation and live metric reporting.",
)

# Initialize OpenTelemetry Distributed Tracing & auto-instrumentation
setup_tracing(app, service_name="devops-super-platform-app")
tracer = get_tracer()


class HealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: float


START_TIME = time.time()


@app.get("/healthz", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Kubernetes liveness and readiness probe endpoint."""
    return {
        "status": "healthy",
        "version": app.version,
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }


@app.get("/metrics", tags=["Observability"])
def metrics():
    """Prometheus metrics scrape endpoint."""
    return get_metrics_response()


@app.get("/", tags=["General"])
def read_root():
    """Base API endpoint."""
    REQUEST_COUNT.labels(method="GET", endpoint="/", status="200").inc()
    return {
        "message": "Welcome to the Zero-Trust DevOps Platform API",
        "version": app.version,
    }


@app.get("/simulate/error", tags=["Testing"])
def simulate_error():
    """Simulates a 500 Internal Error to test Argo Rollouts automatic canary rollbacks."""
    REQUEST_COUNT.labels(method="GET", endpoint="/simulate/error", status="500").inc()
    with tracer.start_as_current_span("simulate_failure"):
        raise HTTPException(
            status_code=500, detail="Synthetic failure triggered for rollback testing."
        )


@app.get("/simulate/latency", tags=["Testing"])
def simulate_latency(seconds: float = 1.5):
    """Simulates processing delay to trigger latency threshold alerts."""
    with tracer.start_as_current_span("simulate_latency_delay"):
        time.sleep(seconds)
    REQUEST_COUNT.labels(method="GET", endpoint="/simulate/latency", status="200").inc()
    return {"status": "delayed", "latency_seconds": seconds}