import inspect
import traceback
import functools
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar, Generic
import cProfile, pstats, io
from pstats import SortKey

from tabulate import tabulate

T = TypeVar('T')


class NonNull(Generic[T]):
    pass


def to_string(decorated_class):
    def __str__(self):
        attributes = [attr for attr in dir(self) if
                      not attr.startswith("_") and
                      not (
                          hasattr(self.__dict__[attr], "__call__")
                          if attr in self.__dict__
                          else hasattr(decorated_class.__dict__[attr],
                                       "__call__"))
                      ]
        output_format = [
            f"{attr}={self.__dict__[attr]}"
            if attr in self.__dict__
            else f"{attr}={decorated_class.__dict__[attr]}"
            for attr in attributes]
        return f"{decorated_class.__name__}@[{', '.join(output_format)}]"

    decorated_class.__str__ = __str__
    return decorated_class


def constructor(decorated_class):
    required_fields = [F for F, T in
                       decorated_class.__dict__["__annotations__"].items() if
                       "__origin__" in T.__dict__ and T.__dict__[
                           "__origin__"] == NonNull]
    original_init = decorated_class.__init__
    attributes = [name for name in decorated_class.__dict__ if
                  not name.startswith('_')]
    if '__annotations__' in decorated_class.__dict__:
        for attr_name in decorated_class.__dict__['__annotations__']:
            if attr_name not in attributes:
                attributes.append(attr_name)

    def __init__(self, *args, **kwargs):
        for attr_name, value in zip(attributes, args):
            if attr_name in required_fields and value is None:
                raise ValueError(f"Field {attr_name} is marked as non-null")
            setattr(self, attr_name, value)
        for tentative_name, value in kwargs.items():
            if tentative_name in required_fields and value is None:
                raise ValueError(
                    f"Field {tentative_name} is marked as non-null")
            if tentative_name in attributes:
                setattr(self, tentative_name, value)

    __init__.__doc__ = original_init.__doc__
    decorated_class.__init__ = __init__
    return decorated_class


def equals_and_hashcode(decorated_class):
    def __eq__(self, other):
        same_class = getattr(self, "__class__") == getattr(other, "__class__")
        same_attrs = getattr(self, "__dict__") == getattr(other, "__dict__")
        return same_class and same_attrs

    def __hash__(self):
        attributes = tuple(sorted(tuple(getattr(self, "__dict__").keys())))
        return hash(attributes)

    decorated_class.__hash__ = __hash__
    decorated_class.__eq__ = __eq__
    return decorated_class


def data(decorated_class):
    decorated_class = to_string(decorated_class)
    decorated_class = constructor(decorated_class)
    decorated_class = equals_and_hashcode(decorated_class)
    return decorated_class


def singleton(cls):
    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if not wrapper_singleton.instance:
            try:
                wrapper_singleton.instance = cls(*args, **kwargs)
            except TypeError:
                # TODO test this case, do we really want to make it a dataclass?
                wrapper_singleton.instance = data(cls)(*args, **kwargs)
        return wrapper_singleton.instance

    wrapper_singleton.instance = None
    return wrapper_singleton


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


def timeit(_func=None, *, timer=time.perf_counter):
    def decorator_timeit(func):
        @functools.wraps(func)
        def wrapper_timeit(*args, **kwargs):
            start = timer()
            ret = func(*args, **kwargs)
            end = timer()
            print(f"{func.__name__} executed in {end - start} seconds")
            return ret

        return wrapper_timeit

    if _func is None:
        return decorator_timeit
    else:
        return decorator_timeit(_func)


@singleton
@data
class PerformanceCounter:
    perf_dict: dict


PerformanceCounter({})


def access_counter(decorated_fn):
    class AccessCounter:

        def __init__(self, delegate, name):
            PerformanceCounter().perf_dict[self] = {"delegate": delegate,
                                                    "name": name, "nReads": 0,
                                                    "nWrites": 0}

        def __getitem__(self, item):
            PerformanceCounter().perf_dict[self]["nReads"] += 1
            return PerformanceCounter().perf_dict[self]["delegate"][item]

        def __setitem__(self, key, value):
            PerformanceCounter().perf_dict[self]["nWrites"] += 1
            PerformanceCounter().perf_dict[self]["delegate"][key] = value

        def __getattr__(self, item):
            PerformanceCounter().perf_dict[self]["nReads"] += 1
            return PerformanceCounter().perf_dict[self][
                "delegate"].__getattribute__(
                item)

        def __setattr__(self, key, value):
            PerformanceCounter().perf_dict[self]["nWrites"] += 1
            return PerformanceCounter().perf_dict[self]["delegate"].__setattr__(
                key, value)

    @functools.wraps(decorated_fn)
    def wrapper_access_counter(*args, **kwargs):
        new_args = []
        for arg, arg_name in zip(args,
                                 inspect.getfullargspec(decorated_fn).args):
            new_args.append(AccessCounter(delegate=arg, name=arg_name))
        ret = decorated_fn(*new_args, **kwargs)
        if new_args:
            print(f"data access summary for function: {decorated_fn.__name__}")
            perf_data = [[PerformanceCounter().perf_dict[arg]["name"],
                          PerformanceCounter().perf_dict[arg]["nReads"],
                          PerformanceCounter().perf_dict[arg]["nWrites"]] for
                         arg in
                         new_args]
            print(tabulate(perf_data, headers=["Arg Name", "nReads", "nWrites"],
                           tablefmt="grid"))

        return ret

    return wrapper_access_counter


def hotspots(_func=None, *, n_runs=1, top_n=10):
    def decorator_hotspots(func):
        @functools.wraps(func)
        def wrapper_hotspots(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()
            ret = None
            for n in range(n_runs):
                ret = func(*args, **kwargs)
            pr.disable()
            pstats.Stats(pr).strip_dirs().sort_stats(
                SortKey.CUMULATIVE).print_stats(top_n)
            return ret

        return wrapper_hotspots

    if _func is None:
        return decorator_hotspots
    else:
        return decorator_hotspots(_func)


def profile(decorated_fn=None, *, n_runs=1, top_n=10):
    decorated_class = access_counter(decorated_fn)
    decorated_class = hotspots(decorated_class)
    return decorated_class


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
