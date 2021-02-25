import functools
import traceback


def silent_catch(_func=None, *, exception=None):
    if not exception:
        exception = Exception
    if type(exception) == list:
        exception = tuple(exception)

    def decorator_silent_catch(func):
        @functools.wraps(func)
        def wrapper_silent_catch(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception:
                pass

        return wrapper_silent_catch

    if _func is None:
        return decorator_silent_catch
    else:
        return decorator_silent_catch(_func)


def catch(_func=None, *, exception=None, handler=None):
    if not exception:
        exception = Exception
    if type(exception) == list:
        exception = tuple(exception)

    def decorator_catch(func):
        @functools.wraps(func)
        def wrapper_catch(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as e:
                if not handler:
                    traceback.print_exc()
                else:
                    handler(e)

        return wrapper_catch

    if _func is None:
        return decorator_catch
    else:
        return decorator_catch(_func)
