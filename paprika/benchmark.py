import cProfile
import functools
import inspect
import pstats
import time
from pstats import SortKey

from tabulate import tabulate


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class PerformanceCounter(Singleton):
    perf_dict = {}


def timeit(_func=None, *, timer=time.perf_counter, handler=None):
    def decorator_timeit(func):
        @functools.wraps(func)
        def wrapper_timeit(*args, **kwargs):
            start = timer()
            ret = func(*args, **kwargs)
            end = timer()
            run_time = end - start
            if handler:
                handler(func.__name__, run_time)
            print(f"{func.__name__} executed in {run_time} seconds")
            return ret

        return wrapper_timeit

    if _func is None:
        return decorator_timeit
    else:
        return decorator_timeit(_func)


def dispatch_access_counter_results(func, new_args, test_mode, test_handler):
    print(f"data access summary for function: {func.__name__}")
    if test_mode:
        test_handler(
            {
                PerformanceCounter()
                .perf_dict[arg]["name"]: PerformanceCounter()
                .perf_dict[arg]
                for arg in new_args
            }
        )
    perf_data = [
        [
            PerformanceCounter().perf_dict[arg]["name"],
            PerformanceCounter().perf_dict[arg]["nReads"],
            PerformanceCounter().perf_dict[arg]["nWrites"],
        ]
        for arg in new_args
    ]
    print(
        tabulate(
            perf_data,
            headers=["Arg Name", "nReads", "nWrites"],
            tablefmt="grid",
        )
    )


class AccessCounter:
    def __init__(self, delegate, name):
        PerformanceCounter().perf_dict[self] = {
            "delegate": delegate,
            "name": name,
            "nReads": 0,
            "nWrites": 0,
        }

    def __getitem__(self, item):
        PerformanceCounter().perf_dict[self]["nReads"] += 1
        return PerformanceCounter().perf_dict[self]["delegate"][item]

    def __setitem__(self, key, value):
        PerformanceCounter().perf_dict[self]["nWrites"] += 1
        PerformanceCounter().perf_dict[self]["delegate"][key] = value

    def __getattr__(self, item):
        PerformanceCounter().perf_dict[self]["nReads"] += 1
        return PerformanceCounter().perf_dict[self]["delegate"].__getattribute__(item)

    def __setattr__(self, key, value):
        PerformanceCounter().perf_dict[self]["nWrites"] += 1
        return PerformanceCounter().perf_dict[self]["delegate"].__setattr__(key, value)


def access_counter(_func=None, *, test_mode=False, test_handler=None):
    def decorator_access_counter(func):
        @functools.wraps(func)
        def wrapper_access_counter(*args, **kwargs):
            new_args = []
            for arg, arg_name in zip(args, inspect.getfullargspec(func).args):
                new_args.append(AccessCounter(delegate=arg, name=arg_name))
            ret = func(*new_args, **kwargs)
            if new_args:
                dispatch_access_counter_results(func, new_args, test_mode, test_handler)

            return ret

        return wrapper_access_counter

    if _func is None:
        return decorator_access_counter
    else:
        return decorator_access_counter(_func)


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
            pstats.Stats(pr).strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(
                top_n
            )
            return ret

        return wrapper_hotspots

    if _func is None:
        return decorator_hotspots
    else:
        return decorator_hotspots(_func)


def profile(decorated_fn=None, *, n_runs=1, top_n=10):
    decorated_class = access_counter(decorated_fn)
    decorated_class = hotspots(decorated_class, n_runs=n_runs, top_n=top_n)
    return decorated_class
