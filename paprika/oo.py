import functools
import pickle
from typing import Type, TypeVar, Generic

T = TypeVar("T")


class NonNull(Generic[T]):
    pass


def to_string(decorated_class):
    def __str__(self):
        attributes = [
            attr
            for attr in dir(self)
            if not attr.startswith("_")
            and not (
                hasattr(self.__dict__[attr], "__call__")
                if attr in self.__dict__
                else hasattr(decorated_class.__dict__[attr], "__call__")
            )
        ]
        output_format = [
            f"{attr}={self.__dict__[attr]}"
            if attr in self.__dict__
            else f"{attr}={decorated_class.__dict__[attr]}"
            for attr in attributes
        ]
        return f"{decorated_class.__name__}@[{', '.join(output_format)}]"

    decorated_class.__str__ = __str__
    return decorated_class


def collect_attributes(decorated_class):
    attributes = [name for name in decorated_class.__dict__ if not name.startswith("_")]
    if "__annotations__" in decorated_class.__dict__:
        for attr_name in decorated_class.__dict__["__annotations__"]:
            if attr_name not in attributes:
                attributes.append(attr_name)
    return attributes


def find_required_fields(decorated_class):
    return [
        F
        for F, T in decorated_class.__dict__["__annotations__"].items()
        if hasattr(T, "__dict__") \
            and "__origin__" in T.__dict__ \
            and T.__dict__["__origin__"] == NonNull
    ]


def bind_fields(inst, fields, attributes, required_fields, kwargs=False):
    for attr_name, value in fields:
        if attr_name in required_fields and value is None:
            raise ValueError(f"Field {attr_name} is marked as non-null")
        if not kwargs or (kwargs and attr_name in attributes):
            setattr(inst, attr_name, value)


def generate_generic_init(attributes, required_fields):
    def __init__(self, *args, **kwargs):
        bind_fields(self, zip(attributes, args), attributes, required_fields)
        bind_fields(self, kwargs.items(), attributes, required_fields, True)

    return __init__


def constructor(decorated_class):
    required_fields = find_required_fields(decorated_class)
    attributes = collect_attributes(decorated_class)

    decorated_class.__init__ = generate_generic_init(attributes, required_fields)
    return decorated_class


def equals_and_hashcode(decorated_class):
    def __eq__(self, other):
        same_class = getattr(self, "__class__") == getattr(other, "__class__")
        same_attrs = getattr(self, "__dict__") == getattr(other, "__dict__")
        return same_class and same_attrs

    def __hash__(self):
        attributes = tuple([getattr(self, "__dict__")[key] for key in
                            sorted(getattr(self, "__dict__").keys())])
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


def pickled(decorated_class=None, protocol=None):
    def decorator(decorated_class):
        def __dump__(self, file_path):
            with open(file_path, "wb") as f:
                pickle.dump(self, f, protocol=protocol)

        @staticmethod
        def __load__(file_path):
            with open(file_path, "rb") as f:
                return pickle.load(f)

        decorated_class.__dump__ = __dump__
        decorated_class.__load__ = __load__

        return decorated_class

    if decorated_class is not None:
        return decorator(decorated_class)

    return decorator
