from copy import copy, deepcopy
from enum import StrEnum


class MetaHeader(StrEnum):
    NORMAL_MESSAGE = "NORMAL_MESSAGE"
    INITIALIZATION_MESSAGE = "INITIALIZATION_MESSAGE"
    ALARM_MESSAGE = "ALARM_MESSAGE"


class Message:

    next_message_id = 1

    def __init__(
        self,
        source=None,
        destination=None,
        nexthop=None,
        header="",
        meta_header=MetaHeader.NORMAL_MESSAGE,
        data=None,
        meta_data=None,
    ):
        """
        Initialize a Message object.

        :param source: The source of the message.
        :type source: Any
        :param destination: The destination of the message.
        :type destination: Any
        :param nexthop: The next hop for the message.
        :type nexthop: Any
        :param header: The header of the message.
        :type header: str
        :param meta_header: The meta header of the message.
        :type meta_header: MetaHeader
        :param data: The data associated with the message.
        :type data: dict
        :param meta_data: The meta data associated with the message. This is meant to be used by the simulation.
        :type meta_data: dict
        """
        self.source = source
        self.destination = destination
        self.nexthop = nexthop
        self.header = header
        self.data = data or dict()
        self.meta_header = meta_header
        self.meta_data = meta_data or dict()
        self.id = self.__class__.next_message_id
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

    def copy(self):
        """
        Create a copy of the Message object.
        """
        # nodes are protected from copying by __deepcopy__()
        copy_data = deepcopy(self.data)
        new_message = copy(self)
        new_message.data = copy_data
        new_message.id = self.__class__.next_message_id
        self.__class__.next_message_id += 1

        return new_message
