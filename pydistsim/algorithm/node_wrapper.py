from functools import cached_property
from random import randint
from typing import TYPE_CHECKING, Any, Union

from pydistsim.logging import logger

if TYPE_CHECKING:
    from pydistsim.algorithm.node_algorithm import StatusValues
    from pydistsim.network import Node
    from pydistsim.network.network import NetworkType


class _NodeWrapper:
    """
    Wrapper class for a node that with controlled access to its attributes.

    Access control is done by defining the attributes that can be accessed in the :attr:`accessible_get` and
    :attr:`accessible_set` class attributes.

    New attributes will be kept only in the wrapper object, while the base node object will remain unchanged except for
    the attributes that are allowed to be changed.
    """

    accessible_get = ()
    "Attributes that can be 'read' from the node base object."

    accessible_set = ()
    "Attributes that can be 'read' or 'written' to the node base object."

    def __init__(self, node: "Node", manager: "WrapperManager", **configs):
        self._node = node
        self._manager = manager
        self._configs = configs

    def __getattr__(self, item):
        if item in self._configs:
            return self._configs[item]
        elif item in self.accessible_get or item in self.accessible_set:
            return getattr(self._node, item)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {item}")

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.accessible_set:
            setattr(self._node, name, value)
        else:
            super().__setattr__(name, value)

    def __repr__(self):
        return self._node.__repr_str__(self.id)

    def __deepcopy__(self, memo):
        # Do not copy the object, just return the same object
        memo[id(self)] = self
        return self

    def __copy__(self):
        # Do not copy the object, just return the same object
        return self

    def unbox(self) -> "Node":
        return self._node

    @property
    def id(self):
        raise AttributeError("Stub method. Raise AttributeError to trigger the __getattr__ method.")


class NeighborLabel(_NodeWrapper):
    """
    Class that represents a neighbor of a node. It is used to represent the knowledge that a node has about its
    neighbors.
    """

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

    accessible_get = (
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

        Keep in mind that `neighbor.id` is only a label for the neighbor, it's local to the node and it's only
        guaranteed to be unique among the neighbors of the node.

        :return: The out-neighbors of the node.
        :rtype: set[NeighborAccess]
        """

        return set(self.__out_neighbors_dict.values())

    def in_neighbors(self) -> set["NeighborLabel"]:
        """
        Get the in-neighbors of the node. If the network is not directed, the in-neighbors are the same as the
        out-neighbors.

        Keep in mind that `neighbor.id` is only a label for the neighbor, it's local to the node and it's only
        guaranteed to be unique among the neighbors of the node.

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
        if "id" not in self._node.memory:
            logger.warning(
                "Node's id do not correspond to the real id of the node. It can't be used to distinguish nodes from "
                "each other as it is not unique unless restriction InitialDistinctValues is applied (or each node has a "
                "unique id set in memory)."
            )
            return self._rand_id

        return self._node.memory["id"]

    @property
    def status(self) -> "StatusValues":
        return self._node.status

    @status.setter
    def status(self, value: "StatusValues"):
        self._node.status = value

    @property
    def memory(self):
        return self._node.memory

    @memory.setter
    def memory(self, value: dict):
        self._node.memory = value

    @property
    def clock(self):
        return self._node.clock

    ###### Private methods ######

    @cached_property
    def __out_neighbors_dict(self) -> dict["Node", "NeighborLabel"]:
        return self._manager.node_out_neighbor_labels[self._node]

    @cached_property
    def __in_neighbors_dict(self) -> dict["Node", "NeighborLabel"]:
        if not self._node.network.is_directed():
            return self.__out_neighbors_dict  # Bidirectional links, same neighbors and same labels
        else:
            return self._manager.node_in_neighbor_labels[self._node]

    def _get_out_neighbor_proxy(self, node: "Node") -> "NeighborLabel":
        return self.__out_neighbors_dict[node]

    def _get_in_neighbor_proxy(self, node: "Node") -> "NeighborLabel":
        return self.__in_neighbors_dict[node]

    @cached_property
    def _rand_id(self):
        return randint(0, len(self._node.network))


class DMANodeAccess(NodeAccess):
    """
    DMANodeAccess class provides a wrapper for node access with direct memory access.
    This means that the node's memory can be accessed directly without the need to use the `memory` attribute.

    For example, instead of using `node.memory["key"]`, you can use `node.key`.
    This works for both setting and getting.

    The simplest way to use this class is as follows:

    .. code-block:: python

        class MyAlgorithm(NodeAlgorithm):
            class Status(StatusValues):
                ...

            def _create_wrapper_manager(self):
                return self.NODE_WRAPPER_MANAGER_TYPE(self.network, DMANodeAccess)


    For a more complex example, see the Mega-Merger algorithm implemented at
    :mod:`pydistsim.demo_algorithms.santoro2007.mega_merger.algorithm`.
    """

    def __getattr__(self, item):
        if item in self._configs:
            return self._configs[item]
        elif item in self.accessible_get or item in self.accessible_set:
            return getattr(self._node, item)
        elif item in super().__getattribute__("_node").memory:
            return super().__getattribute__("_node").memory[item]
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {item}")

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.accessible_set:
            setattr(self._node, name, value)
        elif name in ("_node", "_manager", "_configs"):
            super().__setattr__(name, value)
        else:
            self._node.memory[name] = value

    @property
    def id(self):
        return self._node.memory["id"]

    @id.setter
    def id(self, value):
        self._node.memory["id"] = value


class SensorNodeAccess(NodeAccess):
    accessible_get = (
        *NodeAccess.accessible_get,  # All attributes from NodeAccess
        "sensors",
        "compositeSensor",
    )


class WrapperManager:
    """
    Node Access class
    -----------------

    A node's own view is a proxy for the node that represents the knowledge of the node.

    `u_own_view` and `v_own_view` are the same object passed as parameters at each algorithm's action:

    .. code-block:: python

        @Status.IDLE
        def receiving(self, node: NodeAccess, message: Message):
                                ↑


    Neighbor Label class
    --------------------

    A label for a neighbor is a proxy for the neighbor that represents the knowledge of the neighbor respect to the
    node.

    Alternatively, `u_label_for_v` and `v_label_for_u` are the objects that are returned when a node asks for its
    neighbors in some way:

    .. code-block:: python

        @Status.IDLE
        def receiving(self, node: NodeAccess, message: Message):
            source = message.source  # The node that sent the message
                ↑

            for neighbor in node.neighbors():
                    ↑
    """

    NODE_ACCESS_TYPE: type[NodeAccess]
    "The class that will be used to wrap the nodes' own view."

    NEIGHBOR_LABEL_TYPE = type[NeighborLabel]
    "The class that will be used to wrap the neighbors' labels."

    def __init__(
        self,
        network: "NetworkType",
        nodeAccessType: type[NodeAccess] = NodeAccess,
        neighborLabelType: type[NeighborLabel] = NeighborLabel,
    ):
        self.network = network
        self.NODE_ACCESS_TYPE = nodeAccessType
        self.NEIGHBOR_LABEL_TYPE = neighborLabelType
        self.node_access_instances = {}
        self.node_out_neighbor_labels = {}
        self.node_in_neighbor_labels = {}

    def get_node_access(self, node: Union["Node", "NodeAccess"]) -> NodeAccess:
        if isinstance(node, NodeAccess):
            return node

        if node not in self.node_access_instances:
            node_access = self.NODE_ACCESS_TYPE(node, self)
            self.node_access_instances[node] = node_access
            self.node_out_neighbor_labels[node] = self.calculate_out_neighbors_dict(node_access)
            if self.network.is_directed():
                self.node_in_neighbor_labels[node] = self.calculate_in_neighbors_dict(node_access)

        return self.node_access_instances[node]

    def calculate_out_neighbors_dict(self, node_access: NodeAccess) -> dict["Node", "NeighborLabel"]:
        return {
            node: self.NEIGHBOR_LABEL_TYPE(node, self, id=i)
            for i, node in enumerate(self.network.out_neighbors(node_access._node))
        }

    def calculate_in_neighbors_dict(self, node_access: NodeAccess) -> dict["Node", "NeighborLabel"]:
        assert self.network.is_directed(), "The network must be directed to calculate in-neighbors."

        return {
            node: self.NEIGHBOR_LABEL_TYPE(node, self, id=i)
            for i, node in enumerate(self.network.in_neighbors(node_access._node))
        }

    def edges(self):
        """
        Returns the edges of the network as a tuple of proxies for the nodes and the labels of the neighbors.
        For each edge `(u, v)`, it returns two tuples:
        - `(u_own_view, v_label_for_u)`
        - `(v_own_view, u_label_for_v)`
        """

        for u, v in self.network.edges():
            u_own_view = self.get_node_access(u)
            v_label_for_u = u_own_view._get_out_neighbor_proxy(v)

            v_own_view = self.get_node_access(v)
            u_label_for_v = v_own_view._get_in_neighbor_proxy(u)

            yield (u_own_view, v_label_for_u), (v_own_view, u_label_for_v)

    def nodes(self):
        """
        Returns the proxies for the nodes in the network.
        """

        for node in self.network.nodes():
            yield self.get_node_access(node)

    def nodes_neighbors(self):
        """
        Returns the proxies for the nodes and the labels of it's neighbors.
        """

        for u in self.network.nodes():
            u_node_access = self.get_node_access(u)
            neighbor_labels = u_node_access.out_neighbors()

            yield u_node_access, neighbor_labels
