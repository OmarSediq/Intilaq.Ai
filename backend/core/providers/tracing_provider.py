# backend/core/providers/tracing_provider.py
import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

logger = logging.getLogger("intilaqai.tracing")

def setup_tracing(service_name: str = "intilaqai-backend", enabled: bool = True) -> Optional[TracerProvider]:

    if not enabled:
        logger.info("Tracing disabled by configuration (enabled=False).")
        return None

    try:
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)

        # OTLP exporter - adjust endpoint / insecure according to your infra
        otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)

        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)

        logger.info("Tracing initialized for service: %s", service_name)
        return provider

    except Exception as exc:
        logger.exception("Failed to setup tracing (falling back to no-tracing): %s", exc)
        return None
