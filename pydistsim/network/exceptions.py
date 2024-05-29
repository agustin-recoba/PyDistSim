from enum import StrEnum


class MessageUndeliverableException(Exception):
    def __init__(self, e, message):
        self.e = e
        self.message = message

    def __str__(self):
        return self.e + repr(self.message)


class NetworkErrorMsg(StrEnum):
    ALGORITHM = (
        "Algorithms must be in tuple (AlgorithmClass,)"
        " or in form: ((AlgorithmClass, params_dict),)."
        "AlgorithmClass should be subclass of Algorithm"
    )
    NODE = "Node is already in another network."
    NODE_SPACE = "Given position is not free space."
    NODE_NOT_IN_NET = "Node not in network."
    ALGORITHM_NOT_FOUND = "Algorithm not found in network."
    LIST_TREE_DOWNSTREAM_ONLY = (
        "Downstream only is not supported for list tree. It's impossible to determine direction."
    )


class NetworkException(Exception):
    """
    Exception class for network-related errors.
    """

    def __init__(self, type_):
        if isinstance(type_, NetworkErrorMsg):
            self.message = type_.value
        else:
            self.message = "Unknown error."

    def __str__(self):
        return self.message
