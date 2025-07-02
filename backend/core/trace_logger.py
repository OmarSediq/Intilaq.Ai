import functools
import inspect
import time
import logging
import pprint

trace_logger = logging.getLogger("intilaqai.trace")


def trace_calls(name=None):
    def decorator(func):
        func_name = name or func.__qualname__

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):

                start = time.perf_counter()


                bound_args = inspect.signature(func).bind(*args, **kwargs)
                bound_args.apply_defaults()
                trace_logger.info(f"[TRACE] Calling async {func_name}()")
                trace_logger.info(f"[TRACE] Arguments: {pprint.pformat(bound_args.arguments)}")

                try:
                    result = await func(*args, **kwargs)
                    duration = time.perf_counter() - start
                    trace_logger.info(f"[TRACE] {func_name}() executed in {duration:.4f} sec")
                    trace_logger.info(f"[TRACE] Returned: {pprint.pformat(result)}")
                    return result
                except Exception as e:
                    trace_logger.exception(f"[TRACE] {func_name}() raised {e}")
                    raise

            return async_wrapper

        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                bound_args = inspect.signature(func).bind(*args, **kwargs)
                bound_args.apply_defaults()
                trace_logger.info(f"[TRACE] Calling sync {func_name}()")
                trace_logger.info(f"[TRACE] Arguments: {pprint.pformat(bound_args.arguments)}")

                try:
                    result = func(*args, **kwargs)
                    duration = time.perf_counter() - start
                    trace_logger.info(f"[TRACE] {func_name}() executed in {duration:.4f} sec")
                    trace_logger.info(f"[TRACE] Returned: {pprint.pformat(result)}")
                    return result
                except Exception as e:
                    trace_logger.exception(f"[TRACE] {func_name}() raised {e}")
                    raise

            return sync_wrapper

    return decorator
