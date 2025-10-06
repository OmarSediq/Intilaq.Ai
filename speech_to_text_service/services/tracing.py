# speech_to_text_service/services/tracing.py
from typing import Optional
import os

def setup_tracing(service_name: str, enabled: bool = True, otlp_endpoint: Optional[str] = None):

    if not enabled:
        return


    try:
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry import trace

        endpoint = otlp_endpoint or os.getenv("OTLP_ENDPOINT")
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint) if endpoint else OTLPSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
    except Exception as e:

        print("Tracing setup skipped/failed:", str(e))
        return
