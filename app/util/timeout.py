import multiprocessing.pool
import functools
import typing


def timeout(max_timeout: float = 5, callback: typing.Callable = None):
    """timeout(max_timeout: float, callback: callable):
        decorator for timeouts, callback is called on TimeoutError if given.

        Notes:
            - Function will be executed until it finishes

        Based on:
            https://stackoverflow.com/a/35139284/11901512
    """

    def timeout_decorator(item):
        """Wrap the original function."""

        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            try:
                pool = multiprocessing.pool.ThreadPool(processes=1)
                async_result = pool.apply_async(item, args, kwargs)
                # raises a TimeoutError if execution exceeds max_timeout
                return async_result.get(max_timeout)
            except multiprocessing.TimeoutError as e:
                if callback:
                    return callback(*args, **kwargs)
                else:
                    raise TimeoutError(e)

        return func_wrapper

    return timeout_decorator
