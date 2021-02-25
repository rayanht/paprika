import functools
import time
from concurrent.futures import ThreadPoolExecutor

_DEFAULT_POOL = ThreadPoolExecutor()


def threaded(f, executor=None):
    @functools.wraps(f)
    def wrapper_threaded(*args, **kwargs):
        return (executor or _DEFAULT_POOL).submit(f, *args, **kwargs)

    return wrapper_threaded


def repeat(n):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            for _ in range(n):
                value = func(*args, **kwargs)
            return value

        return wrapper_repeat

    return decorator_repeat


def sleep_after(duration):
    def decorator_sleep(func):
        @functools.wraps(func)
        def wrapper_sleep(*args, **kwargs):
            ret = func(*args, **kwargs)
            time.sleep(duration)
            return ret

        return wrapper_sleep

    return decorator_sleep


def sleep_before(duration):
    def decorator_sleep(func):
        @functools.wraps(func)
        def wrapper_sleep(*args, **kwargs):
            time.sleep(duration)
            return func(*args, **kwargs)

        return wrapper_sleep

    return decorator_sleep
