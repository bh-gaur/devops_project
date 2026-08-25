import os
import logging
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logger = logging.getLogger("observability.tracing")

_tracer = None

def setup_tracing(app: FastAPI, service_name: str = "devops-super-platform-app") -> None:
    """Configures OpenTelemetry TracerProvider and auto-instruments the FastAPI app."""
    global _tracer
    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
    
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    
    try:
        otlp_exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
        processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(processor)
    except Exception as err:
        logger.warning(f"Failed to initialize OTLP exporter on {otel_endpoint}: {err}")

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(service_name)
    
    # Auto-instrument FastAPI routes
    FastAPIInstrumentor.instrument_app(app)

def get_tracer():
    """Returns the configured OpenTelemetry tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("devops-super-platform-app")
    return _tracer
