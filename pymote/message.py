from copy import copy, deepcopy
from enum import StrEnum


class MetaHeader(StrEnum):
    NORMAL_MESSAGE = "NORMAL_MESSAGE"
    INITALIZATION_MESSAGE = "INITALIZATION_MESSAGE"
    ALARM_MESSAGE = "ALARM_MESSAGE"


class Message:

    def __init__(
        self,
        source=None,
        destination=None,
        nexthop=None,
        header="",
        meta_header=MetaHeader.NORMAL_MESSAGE,
        data={},
    ):
        self.source = source
        self.destination = destination
        self.nexthop = nexthop
        self.header = header
        self.meta_header = meta_header
        self.data = data

    def __repr__(self):
        destination = self.destination
        if self.destination is None:
            destination = "Broadcasted"
        elif (
            isinstance(self.destination, list)
            and len(self.destination) == 1
            and self.destination[0] is None
        ):
            destination = "Broadcasting"
        return (
            "\n------ Message '%s' ------ \n     source = %s \ndestination = %s"
            " \n     header = '%s' \nid(message) = 0x%x>"
        ) % (self.meta_header, self.source, destination, self.header, id(self))

    def copy(self):
        # nodes are protected from copying by __deepcopy__()
        self.data = deepcopy(self.data)
        return copy(self)
