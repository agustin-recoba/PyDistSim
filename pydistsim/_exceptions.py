"""
Custom exceptions for the PyDistSim package.
"""

from enum import StrEnum


class MessageUndeliverableException(Exception):
    def __init__(self, e, message):
        self.e = e
        self.message = message

    def __str__(self):
        return self.e + repr(self.message)


class PyDistSimException(Exception):
    ERRORS: type[StrEnum]

    def __init__(self, type_):
        if isinstance(type_, self.ERRORS):
            self.message = type_.value
        else:
            self.message = "Unknown error."

    def __str__(self):
        return self.message


class NetworkException(PyDistSimException):
    """
    Exception class for network-related errors.
    """

    class ERRORS(StrEnum):
        NODE = "Node is already in another network."
        NODE_SPACE = "Given position is not free space."
        NODE_NOT_IN_NET = "Node not in network."


class SimulationException(PyDistSimException):
    """
    Exception class for simulation-related errors.
    """

    class ERRORS(StrEnum):
        ALGORITHM = (
            "Algorithms must be in tuple (AlgorithmClass,)"
            " or in form: ((AlgorithmClass, params_dict),)."
            "AlgorithmClass should be subclass of BaseAlgorithm"
        )
        ALGORITHM_NOT_FOUND = "Algorithm not found in simulation. Please make sure it is added to the simulation."
