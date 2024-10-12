"""
This module contains the :class:`Message` class, which is used to represent messages in the simulation.
"""

from copy import copy, deepcopy
from enum import StrEnum
from typing import Generic, TypeVar


class MetaHeader(StrEnum):
    NORMAL_MESSAGE = "NORMAL_MESSAGE"
    INITIALIZATION_MESSAGE = "INITIALIZATION_MESSAGE"
    ALARM_MESSAGE = "ALARM_MESSAGE"


T = TypeVar("T")


class Message(Generic[T]):
    """
    The Message class is used to represent messages in the simulation.

    :param destination: The destination of the message.
    :type destination: T
    :param header: The header of the message.
    :type header: str
    :param data: The data associated with the message.
    :type data: dict
    :param source: The source of the message.
    :type source: T
    :param meta_header: The meta header of the message.
    :type meta_header: MetaHeader
    :param meta_data: The meta data associated with the message. This is meant to be used by the simulation.
    :type meta_data: dict
    """

    __slots__ = [
        "destination",
        "header",
        "data",
        "source",
        "meta_header",
        "meta_data",
        "_internal_id",
    ]

    META_HEADERS = MetaHeader
    next_message_id = 1

    def __init__(
        self,
        destination: T = None,
        header=None,
        data=None,
        **kwargs,
    ):
        self.destination: T = destination
        self.header = header or "NO HEADER"
        self.data = data

        self.source: T = kwargs.get("source", None)
        self.meta_header = kwargs.get("meta_header", MetaHeader.NORMAL_MESSAGE)
        self.meta_data = kwargs.get("meta_data", {})

        self._internal_id = self.__class__.next_message_id
        self.__class__.next_message_id += 1

    def __repr__(self):
        destination = self.destination
        if self.destination is None:
            destination = "Broadcasted"
        elif isinstance(self.destination, list) and len(self.destination) == 1 and self.destination[0] is None:
            destination = "Broadcasting"
        return (
            "\n------ Message '%s' ------ \n     source = %s \ndestination = %s"
            " \n     header = '%s' \nid(message) = 0x%x>"
        ) % (self.meta_header, self.source, destination, self.header, id(self))

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]

        # Shallow copy of the object
        copy_m = copy(self)
        memo[id(self)] = copy_m

        copy_m._internal_id = self.__class__.next_message_id
        self.__class__.next_message_id += 1

        # Deep copy of the mutable attributes
        copy_m.source = deepcopy(self.source, memo)
        copy_m.destination = deepcopy(self.destination, memo)
        copy_m.data = deepcopy(self.data, memo)
        copy_m.meta_data = deepcopy(self.meta_data, memo)

        return copy_m

    def copy(self):
        """
        Create a copy of the Message object.
        """
        # nodes are protected from copying by __deepcopy__()
        copy_data = deepcopy(self.data)
        new_message = copy(self)
        new_message.data = copy_data
        new_message._internal_id = self.__class__.next_message_id
        self.__class__.next_message_id += 1

        return new_message
