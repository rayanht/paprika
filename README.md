![A plate filled with paprika spice](static/paprika.jpg)
_Image courtesy of Anna Quaglia (Photographer)_

# Paprika

Paprika is a python library that reduces boilerplate. It is heavily inspired by
Project Lombok.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features & Examples](#features-and-examples)
  - [Object-oriented decorators](#general-utility-decorators)
    - [`@to_string`](#to_string)
    - [`@equals_and_hashcode`](#equals_and_hashcode)
    - [`@data`](#data)
      - [On `@data` and NonNull](#on-data-and-nonnull)
    - [`@singleton`](#singleton)
      - [Important note on combining `@data` and `@singleton`](#important-note-on-combining-data-and-singleton)
  - [General utility decorators](#general-utility-decorators)
    - [`@threaded`](#threaded)
    - [`@repeat`](#repeat)
  - [Benchmark decorators](#benchmark-decorators)
    - [`@timeit`](#timeit)
    - [`@access_counter`](#access_counter)
    - [`@hotspots`](#hotspots)
    - [`@profile`](#profile)
  - [Error-handling decorators](#error-handling-decorators)
    - [`@catch`](#catch)
    - [`@silent_catch`](#silent-catch)
- [Contributing](#contributing)
- [Authors](#authors)
- [License](#license)


## Installation

paprika is available on PyPi.

```bash
$ pip install paprika
```

## Usage

`paprika` is a decorator-only library and all decorators are exposed at the
top-level of the module. If you want to use shorthand notation (i.e. `@data`),
you can import all decorators as follows:

```python3
from paprika import *
```

Alternatively, you can opt to use the longhand notation (i.e. `@paprika.data`)
by importing `paprika` as follows:

```python3
import paprika
```

## Features and Examples

## Object-oriented decorators

### @to_string

The `@to_string` decorator automatically overrides `__str__`

#### Python

```python3
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.__name__}@[name={self.name}, age={self.age}]"
```

#### Python with paprika

```python3
@to_string
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
```

----

### @equals_and_hashcode

The `@equals_and_hashcode` decorator automatically overrides `__eq__`
and `__hash__`

#### Python

```python3
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and
                self.__dict__ == other.__dict__)

    def __hash__(self):
        return hash((self.name, self.age))
```

#### Python with paprika

```python3
@equals_and_hashcode
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
```

---

### @data

The `@data` decorator creates a dataclass by combining `@to_string`
and `@equals_and_hashcode` and automatically creating a constructor!

#### Python

```python3
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.__name__}@[name={self.name}, age={self.age}]"

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and
                self.__dict__ == other.__dict__)

    def __hash__(self):
        return hash((self.name, self.age))
```

#### Python with paprika

```python3
@data
class Person:
    name: str
    age: int
```

#### On @data and NonNull

`paprika` exposes a `NonNull` generic type that can be used in conjunction with
the `@data` decorator to enforce that certain arguments passed to the
constructor are not null. The following snippet will raise a `ValueError`:

```python3
@data
class Person:
    name: NonNull[str]
    age: int

p = Person(name=None, age=42)  # ValueError ❌
```

----

### @singleton

The `@singleton` decorator can be used to enforce that a class only gets
instantiated once within the lifetime of a program. Any subsequent instantiation
will return the original instance.

```python3
@singleton
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

p1 = Person(name="Rayan", age=19)
p2 = Person()
print(p1 == p2 and p1 is p2)  # True ✅
```

`@singleton` can be seamlessly combined with `@data`!

```python3
@singleton
@data
class Person:
    name: str
    age: int

p1 = Person(name="Rayan", age=19)
p2 = Person()
print(p1 == p2 and p1 is p2)  # True ✅
```

#### Important note on combining @data and @singleton

When combining `@singleton` with `@data`, `@singleton` should come
before `@data`. Combining them the other way around will work in most cases but
is not thoroughly tested and relies on assumptions that _might_ not hold.

## General utility decorators

### @threaded

The `@threaded` decorator will run the decorated function in a thread by
submitting it to a `ThreadPoolExecutor`. When the decorated function is called,
it will immediately return a `Future` object. The result can be extracted by
calling `.result()` on that `Future`

```python3
@threaded
def waste_time(sleep_time):
    thread_name = threading.current_thread().name
    time.sleep(sleep_time)
    print(f"{thread_name} woke up after {sleep_time}s!")
    return 42

t1 = waste_time(5)
t2 = waste_time(2)

print(t1)           # <Future at 0x104130a90 state=running>
print(t1.result())  # 42
```

```
ThreadPoolExecutor-0_1 woke up after 2s!
ThreadPoolExecutor-0_0 woke up after 5s!
```

---

### @repeat

The `@repeat` decorator will run the decorated function consecutively, as many
times as specified.

```python3
@repeat(n=5)
def hello_world():
    print("Hello world!")

hello_world()
```

```
Hello world!
Hello world!
Hello world!
Hello world!
Hello world!
```

## Benchmark decorators

### timeit

The `@timeit` decorator times the total execution time of the decorated
function. It uses a `timer::perf_timer` by default but that can be replaced by
any object of type `Callable[None, int]`.

```python3
def time_waster1():
    time.sleep(2)

def time_waster2():
    time.sleep(5)

@timeit
def test_timeit():
    time_waster1()
    time_waster2()
```

```python
test_timeit executed in 7.002189894999999 seconds
```

Here's how you can replace the default timer:

```python
@timeit(timer: lambda: 0) # Or something actually useful like time.time()
def test_timeit():
    time_waster1()
    time_waster2()
```

```python
test_timeit executed in 0 seconds
```

---

### @access_counter

The `@access_counter` displays a summary of how many times each of the
structures that are passed to the decorated function are accessed
(number of reads and number of writes).

```python3
@access_counter
def test_access_counter(list, dict, person, tuple):
    for i in range(500):
        list[0] = dict["key"]
        dict["key"] = person.age
        person.age = tuple[0]


test_access_counter([1, 2, 3, 4, 5], {"key": 0}, Person(name="Rayan", age=19),
                    (0, 0))
```

```
data access summary for function: test
+------------+----------+-----------+
| Arg Name   |   nReads |   nWrites |
+============+==========+===========+
| list       |        0 |       500 |
+------------+----------+-----------+
| dict       |      500 |       500 |
+------------+----------+-----------+
| person     |      500 |       500 |
+------------+----------+-----------+
| tuple      |      500 |         0 |
+------------+----------+-----------+
```

___

### @hotspots

The `@hotspots` automatically runs `cProfiler` on the decorated function and
display the `top_n` (default = 10) most expensive function calls sorted by
cumulative time taken (this metric will be customisable in the future). The
sample error can be reduced by using a higher `n_runs` (default = 1) parameter.

```python3
def time_waster1():
    time.sleep(2)

def time_waster2():
    time.sleep(5)

@hotspots(top_n=5, n_runs=2)  # You can also do just @hotspots
def test_hotspots():
    time_waster1()
    time_waster2()

test_hotspots()
```

```
   11 function calls in 14.007 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        2    0.000    0.000   14.007    7.004 main.py:27(test_hot)
        4   14.007    3.502   14.007    3.502 {built-in method time.sleep}
        2    0.000    0.000   10.004    5.002 main.py:23(time_waster2)
        2    0.000    0.000    4.003    2.002 main.py:19(time_waster1)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

---

### @profile

The `@profile` decorator is simply syntatic sugar that allows to perform both
hotspot analysis and data access analysis. Under the hood, it simply
uses `@access_counter` followed by `@hotspots`.

## Error-handling decorators

### @catch

The `@catch` decorator can be used to wrap a function inside a `try/catch`
block. `@catch` expects to receive in the `exceptions` argument at least one
exception that we want to catch.

If no exception is provided, `@catch` will by default catch _all_ exceptions (
excluding `SystemExit`, `KeyboardInterrupt`
and `GeneratorExit` since they do not subclass the generic `Exception` class).

`@catch` can take a custom exception handler as a parameter. If no handler is
supplied, a stack trace is logged to `stderr` and the program will continue
executing.

```python
@catch(exception=ValueError)
def test_catch1():
    raise ValueError

@catch(exception=[EOFError, KeyError])
def test_catch2():
    raise ValueError

test_catch1()
print("Still alive!")  # This should get printed since we're catching the ValueError.

test_catch2()
print("Still alive?")  # This will not get printed since we're not catching ValueError in this case.
```

```
Traceback (most recent call last):
  File "/Users/rayan/Desktop/paprika/paprika/__init__.py", line 292, in wrapper_catch
    return func(*args, **kwargs)
  File "/Users/rayan/Desktop/paprika/main.py", line 29, in test_exception1
    raise ValueError
ValueError

Still alive!

Traceback (most recent call last):
  File "/Users/rayan/Desktop/paprika/main.py", line 40, in <module>
    test_exception2()
  File "/Users/rayan/Desktop/paprika/paprika/__init__.py", line 292, in wrapper_catch
    return func(*args, **kwargs)
  File "/Users/rayan/Desktop/paprika/main.py", line 37, in test_exception2
    raise ValueError
ValueError
```

#### Using a custom exception handler

If provided, a custom exception handler must be of
type `Callable[Exception, Generic[T]]`. In other words, its signature must take
one parameter of type Exception.

```python
@catch(exception=ValueError,
       handler=lambda x: print(f"Ohno, a {repr(x)} was raised!"))
def test_custom_handler():
    raise ValueError

test_custom_handler()
```

```
Ohno, a ValueError() was raised!
```

---

### @silent_catch

The `@silent_catch` decorator is very similar to the `@catch` decorator in its
usage. It takes one or more exceptions but then simply catches them silently.

```python
@silent_catch(exception=[ValueError, TypeError])
def test_silent_catch():
    raise TypeError

test_silent_catch()
print("Still alive!")
```

```
Still alive!
```

## Contributing

Encountered a bug? Have an idea for a new feature? This project is open to all
sorts of contribution! Feel free to head to the `Issues` tab and describe your
request!

## Authors

* **Rayan Hatout** - [GitHub](https://github.com/rayanht)
  | [Twitter](https://twitter.com/rayanhtt)
  | [LinkedIn](https://www.linkedin.com/in/rayan-hatout/)

See also the list of [contributors](https://github.com/rayanht/paprika) who
participated in this project.

## License

This project is licensed under the MIT License - see
the [LICENSE.md](LICENSE.md) file for details
