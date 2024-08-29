from functools import cached_property
from random import randint
from typing import TYPE_CHECKING, Any

from pydistsim.logging import logger

if TYPE_CHECKING:
    from pydistsim.network import Node


class _NodeWrapper:
    """
    Wrapper class for a node that with controlled access to its attributes.

    Access control is done by defining the attributes that can be accessed in the :attr:`accessible_get` and
    :attr:`accessible_set` class attributes.

    New attributes will be kept only in the wrapper object, while the base node object will remain unchanged except for
    the attributes that are allowed to be changed.
    """

    accessible_get = ("id",)
    "Attributes that can be 'read' from the node base object."

    accessible_set = ()
    "Attributes that can be 'read' or 'written' to the node base object."

    def __init__(self, node: "Node", **configs):
        self.node = node
        self.configs = configs

    def __getattr__(self, item):
        if item in self.configs:
            return self.configs[item]
        elif item in self.accessible_get or item in self.accessible_set:
            return getattr(self.node, item)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {item}")

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.accessible_set:
            setattr(self.node, name, value)
        else:
            super().__setattr__(name, value)

    def __repr__(self):
        return self.node.__repr_str__(self.id)

    def __deepcopy__(self, memo):
        # Do not copy the object, just return the same object
        memo[id(self)] = self
        return self

    def __copy__(self):
        # Do not copy the object, just return the same object
        return self

    def unbox(self) -> "Node":
        return self.node

    @property
    def id(self):
        raise AttributeError("Stub method. Raise AttributeError to trigger the __getattr__ method.")


class NeighborLabel(_NodeWrapper):
    """
    Class that represents a neighbor of a node. It is used to represent the knowledge that a node has about its
    neighbors.
    """

    accessible_get = ("id",)

    def __repr__(self):
        return f"Neighbor(label={self.id})"

    @property
    def id(self):
        logger.warning(
            "Neighbor's id do not correspond to the real id of the node. It can be used to distinguish "
            "neighbors from each other."
        )
        return super().id


class NodeAccess(_NodeWrapper):
    """
    Class used to control the access to a node's attributes.

    For full node access, use the :meth:`unbox` method. Be aware that such access may break the knowledge restrictions
    of the algorithm.
    """

    NEIGHBOR_LABEL_CLASS: type[NeighborLabel] = NeighborLabel

    accessible_get = (
        "id",
        "status",
        "memory",
        "clock",
    )

    accessible_set = (
        "status",
        "memory",
    )

    def neighbors(self) -> set["NeighborLabel"]:
        """
        Get the out-neighbors of the node.

        :return: The out-neighbors of the node.
        :rtype: set[NeighborAccess]
        """

        return set(self.__out_neighbors_dict.values())

    def in_neighbors(self) -> set["NeighborLabel"]:
        """
        Get the in-neighbors of the node. If the network is not directed, the in-neighbors are the same as the
        out-neighbors.

        :return: The in-neighbors of the node.
        :rtype: set[NeighborAccess]
        """

        return set(self.__in_neighbors_dict.values())

    out_neighbors = neighbors
    "Alias for out_neighbors."

    @property
    def id(self):
        """
        Get the id of the node. If the node does not have an id in memory, a random id will be generated.
        It is not guaranteed that the id will be unique among all nodes in the network.

        Since the id is a read-only attribute, it is cached to avoid generating a new id every time it is accessed.
        """
        if "id" not in self.node.memory:
            logger.warning(
                "Node's id do not correspond to the real id of the node. It can't be used to distinguish nodes from "
                "each other as it is not unique unless restriction InitialDistinctValues is applied (or each node has a "
                "unique id set in memory)."
            )
            return self._rand_id

        return self.node.memory["id"]

    ###### Private methods ######

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def __out_neighbors_dict(self) -> dict["Node", "NeighborLabel"]:
        return {
            node: self.NEIGHBOR_LABEL_CLASS(node, id=i)
            for i, node in enumerate(self.node.network.out_neighbors(self.node))
        }

    @cached_property
    def __in_neighbors_dict(self) -> dict["Node", "NeighborLabel"]:
        if not self.node.network.is_directed():
            return self.__out_neighbors_dict  # Bidirectional links, same neighbors and same labels
        else:
            return {
                node: self.NEIGHBOR_LABEL_CLASS(node, id=i)
                for i, node in enumerate(self.node.network.in_neighbors(self.node))
            }

    def _get_out_neighbor_proxy(self, node: "Node") -> "NeighborLabel":
        return self.__out_neighbors_dict[node]

    def _get_in_neighbor_proxy(self, node: "Node") -> "NeighborLabel":
        return self.__in_neighbors_dict[node]

    @cached_property
    def _rand_id(self):
        return randint(0, len(self.node.network))

    __wrapped_nodes__ = {}
    "Memoization of the wrapped nodes. Used to avoid creating multiple wrappers for the same node."

    def __new__(cls, node: "Node", *args, **configs):
        "A NodeProxy wrapper is created only once for each node."

        if node in cls.__wrapped_nodes__:
            wrapped_node: cls = cls.__wrapped_nodes__[node]
            if cls != wrapped_node.__class__:
                logger.trace(
                    f"Node {node} was wrapped with a different class. "
                    f"Changing from {wrapped_node.__class__.__name__} to {cls.__name__}."
                )
                wrapped_node.__class__ = cls

            return wrapped_node

        cls.__wrapped_nodes__[node] = super().__new__(cls, *args, **configs)
        return cls.__wrapped_nodes__[node]

    @classmethod
    def _clear_from_memoization(cls, node: "Node"):
        cls.__wrapped_nodes__.pop(node, None)


class SensorNodeAccess(NodeAccess):
    accessible_get = (
        *NodeAccess.accessible_get,  # All attributes from NodeAccess
        "sensors",
        "compositeSensor",
    )
