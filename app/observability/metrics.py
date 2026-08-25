from fastapi import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Prometheus Metrics definitions
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total HTTP requests handled by the application",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "HTTP request latency distribution in seconds",
    ["endpoint"],
)

def get_metrics_response() -> Response:
    """Generates Prometheus scrapable metrics payload."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
