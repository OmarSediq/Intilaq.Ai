# infrastructure/observability/tracing.py
import functools
import inspect
import time
import logging
import pprint

trace_logger = logging.getLogger("notification_service.trace")

def _safe_repr(obj, max_len=1000):
    try:
        r = pprint.pformat(obj)
    except Exception:
        try:
            r = repr(obj)
        except Exception:
            r = "<unrepresentable>"
    if len(r) > max_len:
        return r[:max_len] + "...(truncated)"
    return r

def trace_calls(name=None):
    def decorator(func):
        func_name = name or func.__qualname__

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                trace_logger.info("[TRACE] Calling async %s()", func_name)
                try:
                    result = await func(*args, **kwargs)
                    duration = time.perf_counter() - start
                    trace_logger.info("[TRACE] %s() executed in %.4f sec", func_name, duration)
                    return result
                except Exception:
                    trace_logger.exception("[TRACE] %s() failed", func_name)
                    raise
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                trace_logger.info("[TRACE] Calling sync %s()", func_name)
                try:
                    result = func(*args, **kwargs)
                    duration = time.perf_counter() - start
                    trace_logger.info("[TRACE] %s() executed in %.4f sec", func_name, duration)
                    return result
                except Exception:
                    trace_logger.exception("[TRACE] %s() failed", func_name)
                    raise
            return sync_wrapper
    return decorator
