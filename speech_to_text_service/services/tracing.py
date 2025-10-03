# speech_to_text_service/core/tracing.py
import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def setup_tracing(service_name: str = "whisper-service", enabled: bool = True):
    """
    Configure OpenTelemetry tracing for this service.
    Safe to call; if enabled=False it will be a no-op.
    """
    if not enabled:
        return None

    # use env or default to docker-compose jaeger service
    jaeger_endpoint = os.getenv("JAEGER_OTLP_ENDPOINT", "http://jaeger:4317")
    resource = Resource.create({"service.name": service_name})

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    otlp_exporter = OTLPSpanExporter(endpoint=jaeger_endpoint, insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    return trace.get_tracer(service_name)
