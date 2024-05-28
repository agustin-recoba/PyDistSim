from collections.abc import Iterable
from typing import TYPE_CHECKING, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def pydistsim_equal_objects(obj1, obj2):
    """
    Compare two objects and their attributes, but allow for non immutable
    attributes to be equal up to their class.
    """
    classes = obj1.__class__ == obj2.__class__
    attr_names = attr_values = True
    if isinstance(obj1, object) and isinstance(obj2, object):
        attr_names = set(obj1.__dict__.keys()) == set(obj2.__dict__.keys())
    types = (str, tuple, int, int, bool, float, frozenset, bytes, complex)
    for key, value in list(obj1.__dict__.items()):
        other_value = getattr(obj2, key, None)
        if (
            isinstance(value, types) and value != other_value
        ) or value.__class__ != other_value.__class__:
            attr_values = False
            break
    return classes and attr_names and attr_values


def with_typehint(baseclass: type[T]) -> type[T]:
    """
    Useful function to make mixins with baseclass typehint without actually inheriting from it.
    """
    if TYPE_CHECKING:
        return baseclass
    return object


def first(iterable: Iterable[T], default: U | None = None) -> T | U | None:
    """
    Return the first item in an iterable, or a default value if the iterable is empty.

    :param iterable: The iterable to get the first item from.
    :type iterable: Iterable[T]
    :param default: The default value to return if the iterable is empty.
    :type default: U | None

    :return: The first item in the iterable, or the default value if the iterable is empty.
    :rtype: T | U | None
    """

    iterator = iter(iterable)
    return next(iterator, default)
