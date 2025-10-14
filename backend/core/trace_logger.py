import functools
import inspect
import time
import logging
import pprint

trace_logger = logging.getLogger("intilaqai.trace")

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
                # آمن: استخدم bind_partial واحتواء الاستثناء
                try:
                    bound = inspect.signature(func).bind_partial(*args, **kwargs)
                    bound.apply_defaults()
                    bound_arguments = dict(bound.arguments)
                except Exception as e:
                    bound_arguments = {"__bind_error": repr(e), "args": _safe_repr(args, 400), "kwargs": _safe_repr(kwargs, 400)}

                trace_logger.info("[TRACE] Calling async %s()", func_name)
                trace_logger.info("[TRACE] Arguments: %s", _safe_repr(bound_arguments, 800))

                try:
                    result = await func(*args, **kwargs)
                    duration = time.perf_counter() - start
                    trace_logger.info("[TRACE] %s() executed in %.4f sec", func_name, duration)
                    trace_logger.info("[TRACE] Returned: %s", _safe_repr(result, 800))
                    return result
                except Exception as e:
                    trace_logger.exception("[TRACE] %s() raised %s", func_name, repr(e))
                    raise

            return async_wrapper

        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    bound = inspect.signature(func).bind_partial(*args, **kwargs)
                    bound.apply_defaults()
                    bound_arguments = dict(bound.arguments)
                except Exception as e:
                    bound_arguments = {"__bind_error": repr(e), "args": _safe_repr(args, 400), "kwargs": _safe_repr(kwargs, 400)}

                trace_logger.info("[TRACE] Calling sync %s()", func_name)
                trace_logger.info("[TRACE] Arguments: %s", _safe_repr(bound_arguments, 800))

                try:
                    result = func(*args, **kwargs)
                    duration = time.perf_counter() - start
                    trace_logger.info("[TRACE] %s() executed in %.4f sec", func_name, duration)
                    trace_logger.info("[TRACE] Returned: %s", _safe_repr(result, 800))
                    return result
                except Exception as e:
                    trace_logger.exception("[TRACE] %s() raised %s", func_name, repr(e))
                    raise

            return sync_wrapper

    return decorator
