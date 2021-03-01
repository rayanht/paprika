import functools
import traceback


def silent_catch(_func=None, *, exception=None):
    return catch(_func=_func, exception=exception, silent=True)    
    

def catch(_func=None, *, exception=None, handler=None, silent=False):
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
                if not silent:
                    if not handler:
                        traceback.print_exc()
                    else:
                        handler(e)

        return wrapper_catch

    if _func is None:
        return decorator_catch
    else:
        return decorator_catch(_func)
