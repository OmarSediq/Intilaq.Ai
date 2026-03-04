from Core.tracing import trace_calls
import inspect

class TraceableService:
    def __init_subclass__(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value) and not attr_name.startswith("_"):
                setattr(cls, attr_name, trace_calls()(attr_value))
