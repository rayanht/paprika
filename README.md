Paprika is a python library that reduces boilerplate. Heavily inspired by
Project Lombok.

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

## Features & Examples

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

#### Footnote on @data and NonNull

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
will return the same original instance.

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

---

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


## Authors

* **Rayan Hatout** - [GitHub](https://github.com/rayanht)
  | [Twitter](https://twitter.com/rayanhtt)
  | [LinkedIn](https://www.linkedin.com/in/rayan-hatout/)

See also the list of [contributors](https://github.com/rayanht/paprika) who
participated in this project.

## License

This project is licensed under the MIT License - see
the [LICENSE.md](LICENSE.md) file for details