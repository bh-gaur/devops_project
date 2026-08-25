"""
Observability package for Autonomous DevOps Platform API.
Provides distributed tracing (OpenTelemetry) and metrics reporting (Prometheus).
"""

from app.observability.tracing import setup_tracing, get_tracer
from app.observability.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    get_metrics_response,
)

__all__ = [
    "setup_tracing",
    "get_tracer",
    "REQUEST_COUNT",
    "REQUEST_LATENCY",
    "get_metrics_response",
]
