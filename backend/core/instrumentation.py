from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

def instrument_app(app, enabled: bool = True):
    if not enabled:
        return
    FastAPIInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()
