from collections.abc import Callable, Iterable
from itertools import product
from typing import TYPE_CHECKING, Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def pydistsim_equal_objects(obj1, obj2):
    """
    Compare two objects and their attributes, but allow for non immutable
    attributes to be equal up to their class.

    :param obj1: The first object to compare.
    :type obj1: object
    :param obj2: The second object to compare.
    :type obj2: object
    """
    classes = obj1.__class__ == obj2.__class__
    attr_names = attr_values = True
    if isinstance(obj1, object) and isinstance(obj2, object):
        attr_names = set(obj1.__dict__.keys()) == set(obj2.__dict__.keys())
    types = (str, tuple, int, int, bool, float, frozenset, bytes, complex)
    for key, value in list(obj1.__dict__.items()):
        other_value = getattr(obj2, key, None)
        if (isinstance(value, types) and value != other_value) or value.__class__ != other_value.__class__:
            attr_values = False
            break
    return classes and attr_names and attr_values


def with_typehint(baseclass: type[T]) -> type[T]:
    """
    Useful function to make mixins with baseclass typehint without actually inheriting from it.

    :param baseclass: The base class to use as a type hint.
    :type baseclass: type[T]
    :return: The base class if TYPE_CHECKING is True, otherwise object.
    :rtype: type[T]
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


def measure_sortedness(sequence: Iterable[T], key: Callable[[T], Any] = None, reverse: bool = False) -> float:
    """
    Measure the sortedness of a sequence. A higher value means the sequence is more sorted.

    `sortedness = 1 - inversions / (n * (n - 1) / 2)`, so if `sortedness == 1` corresponds to a sorted sequence.


    :param sequence: The sequence to measure the sortedness of.
    :type sequence: Iterable[T]
    :param key: The key function to use to extract a comparison key from each element.
    :type key: Callable[[T], Any]
    :param reverse: Whether to sort the sequence in reverse order.
    :type reverse: bool
    :return: The sortedness of the sequence (between 0 and 1) and the inverted pairs found.
    :rtype: tuple[float, list[tuple[int, int]]]
    """

    if len(sequence) <= 1:
        return 1.0, []

    if not key:
        key = lambda x: x

    if reverse:
        key = lambda x: -key(x)

    sortedness = 0
    inverted_pairs = []
    for pair in product(range(len(sequence)), repeat=2):
        i, j = pair
        if i < j and key(sequence[i]) <= key(sequence[j]):
            sortedness += 1
        elif i != j:
            inverted_pairs.append(pair)

    return (sortedness / (len(sequence) * (len(sequence) - 1) / 2), inverted_pairs)


def len_is_one(iterable):
    """
    Returns true if the iterable has one element without consuming it entirely.
    """
    it = iter(iterable)
    try:
        next(it)
        return not next(it, False)
    except StopIteration:
        return False


def len_is_not_zero(iterable):
    """
    Returns true if the iterable has at least one element without consuming it entirely.
    """
    try:
        next(iter(iterable))
        return True
    except StopIteration:
        return False
