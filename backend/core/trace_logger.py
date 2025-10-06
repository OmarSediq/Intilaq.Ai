# backend/core/tracing_logger.py
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode
import functools
import inspect
import time

def _get_tracer():
    return trace.get_tracer("intilaqai")

def trace_calls(name=None):
    def decorator(func):
        func_name = name or func.__qualname__

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                tracer = _get_tracer()
                with tracer.start_as_current_span(func_name, kind=SpanKind.INTERNAL) as span:
                    try:
                        start = time.perf_counter()
                        result = await func(*args, **kwargs)
                        duration = time.perf_counter() - start
                        span.set_attribute("duration_sec", duration)
                        span.set_attribute("args", str(args))
                        span.set_attribute("kwargs", str(kwargs))
                        return result
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise
            return async_wrapper

        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                tracer = _get_tracer()
                with tracer.start_as_current_span(func_name, kind=SpanKind.INTERNAL) as span:
                    try:
                        start = time.perf_counter()
                        result = func(*args, **kwargs)
                        duration = time.perf_counter() - start
                        span.set_attribute("duration_sec", duration)
                        span.set_attribute("args", str(args))
                        span.set_attribute("kwargs", str(kwargs))
                        return result
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise
            return sync_wrapper
    return decorator
