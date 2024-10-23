from collections import OrderedDict
from itertools import product
from typing import TYPE_CHECKING, Optional, TypeVar

from numpy import array, cos, log2, pi, sign, sin, sqrt
from numpy.random import rand

from pydistsim.logging import logger
from pydistsim.network.network import BidirectionalNetwork, Network
from pydistsim.network.node import Node
from pydistsim.network.rangenetwork import BidirectionalRangeNetwork, RangeNetwork

if TYPE_CHECKING:
    from pydistsim.network.environment import Environment2D
    from pydistsim.network.network import NetworkType
    from pydistsim.network.rangenetwork import RangeNetworkType

T = TypeVar("T", bound="NetworkType")


class NetworkGenerator:
    """
    Class for generating networks with specified properties.

    Instance mode
    -------------

    Usage example:

        >>> net_gen = NetworkGenerator(n_count=45, degree=4, directed=False, enforce_connected=False)
        >>> net = net_gen.generate_random_network()

    The generated network is returned as a :class:`pydistsim.network.rangenetwork.RangeNetwork`
    or :class:`pydistsim.network.rangenetwork.BidirectionalRangeNetwork` object.


    Class mode
    ----------

    Here instancing the class will have no effect at all. The only parameters considered are the ones
    passed to the class methods. The class methods are:

    #. :meth:`generate_complete_network`
    #. :meth:`generate_ring_network`
    #. :meth:`generate_star_network`
    #. :meth:`generate_hypercube_network`
    #. :meth:`generate_mesh_network`

    Usage example:

        >>> net = NetworkGenerator.generate_complete_network(5)



    :param n_count: int, number of nodes, if None, 100 is used
    :param n_min: int, minimum number of nodes, if not set it is equal to n_count
    :param n_max: int, maximum number of nodes, if not set it is equal to n_count
    :param enforce_connected: bool, if True network must be fully connected
    :param degree: int, average number of neighbors per node
    :param comm_range: int, nodes communication range, if None, 100 is used
        and it is a signal that this value can be changed if needed to
        satisfy other wanted properties (connected and degree)
    :param method: str, sufix of the name of the method used to generate network
    :param degree_tolerance: float, tolerance for degree parameter
    :param directed: bool, if True generated network is directed
    :param kwargs: network and node __init__ kwargs i.e.:
        - environment: Environment, environment in which the network should be created, if None
        Environment2D is used
        - rangeType: RangeType
        - algorithms: tuple
        - commRange: int, overrides `comm_range`
        - sensors: tuple
    """

    DIRECTED_NETWORK_T = RangeNetwork
    UNDIRECTED_NETWORK_T = BidirectionalRangeNetwork

    def __init__(
        self,
        n_count=None,
        n_min=None,
        n_max=None,
        enforce_connected=True,
        degree=None,
        comm_range=None,
        method="random_network",
        degree_tolerance=0.5,
        directed=False,
        **kwargs,
    ):
        self.n_count = n_count or 100
        self.n_min = self.n_count if n_min is None else n_min
        self.n_max = self.n_count if n_max is None else n_max
        if self.n_count < self.n_min or self.n_count > self.n_max:
            raise NetworkGeneratorException("Number of nodes (n_count parameter) must be between n_min and n_max.")
        if degree and degree >= self.n_max:
            raise NetworkGeneratorException(
                "Degree %d must be smaller than maximum number of nodes %d." % (degree, self.n_max)
            )
        # TODO: optimize recalculation of edges on bigger commRanges
        if degree:
            logger.warning("Generation could be slow for large degree parameter with bounded n_max.")
        self.enforce_connected = enforce_connected
        self.degree = degree
        self.degree_tolerance = degree_tolerance
        self.directed = directed
        self.comm_range = kwargs.pop("commRange", comm_range)
        # TODO: use subclass based generators instead of method based
        self.generate = self.__getattribute__("generate_" + method)
        self.kwargs = kwargs

    def _create_modify_network(self, net: Optional["RangeNetworkType"] = None, step=1) -> Optional["RangeNetworkType"]:
        """
        Helper method for creating a new network or modifying a given network.

        :param net: NetworkType object, optional
            The network to modify. If None, create a new network from scratch.
        :param step: int, optional
            If step > 0, the new network should be more dense. If step < 0, the new network should be less dense.

        :return: NetworkType object or None
            The modified network if successful, None otherwise.
        """
        if net is None:
            net_class = self.DIRECTED_NETWORK_T if self.directed else self.UNDIRECTED_NETWORK_T
            net = net_class(**self.kwargs)
            for _n in range(self.n_count):
                node = Node(commRange=self.comm_range, **self.kwargs)
                net.add_node(node)
        else:
            if step > 0:
                if len(net) < self.n_max:
                    node = Node(**self.kwargs)
                    net.add_node(node)
                    logger.trace("Added node, number of nodes: {}", len(net))
                elif not self.comm_range:
                    for node in net.nodes():
                        node.commRange += step
                    logger.trace("Increased commRange to {}", node.commRange)
                else:
                    return None
            else:
                min_node = net.nodes_sorted()[0]
                if len(net) > self.n_min and len(net) > 1:
                    net.remove_node(min_node)
                    logger.trace("Removed node, nodes left: {}", len(net))
                elif not self.comm_range:
                    for node in net:
                        node.commRange += step
                    logger.trace("Decreased commRange to {}", node.commRange)
                else:
                    return None
        return net

    def _are_conditions_satisfied(self, net: "RangeNetworkType"):
        """
        Check if the conditions for the network are satisfied.

        :param net: The network to check the conditions for.
        :type net: Network
        :return: The condition value.
        :rtype: int
        """
        cr = net.nodes_sorted()[0].commRange
        if self.enforce_connected and not net.is_connected():
            logger.debug("Not connected")
            return round(0.2 * cr)
        elif self.degree:
            diff = self.degree - net.avg_degree()
            if abs(diff) > self.degree_tolerance:
                logger.debug("Degree not satisfied: {} with {} nodes", net.avg_degree(), len(net))
                diff = sign(diff) * min(
                    max(abs(diff), 3), 7
                )  # If diff is too big, it will be set to 7, if it is too small, it will be set to 3
                condition_returned = round((sign(diff) * (round(diff)) ** 2) * cr / 100)
                logger.debug("Degree condition returned: {}", condition_returned)
                return condition_returned
        return 0

    def generate_random_network(
        self, net: Optional["RangeNetworkType"] = None, max_steps=1000
    ) -> Optional["RangeNetworkType"]:
        """
        Generates a random network with randomly positioned nodes.

        :param net: The network to modify. If not provided, a new network will be created.
        :type net: Optional[RangeNetworkType]
        :param max_steps: The maximum number of steps to take.
        :type max_steps: int
        :return: The generated network, optional.
        :rtype: Optional[RangeNetworkType]
        """
        # TODO: try some more advanced algorithm for situation when
        # both connected network and too small degree are needed
        # that is agnostic to actual dimensions of the environment
        steps = [0]
        while True:
            net = self._create_modify_network(net, steps[-1])
            if not net:
                break
            steps.append(self._are_conditions_satisfied(net))
            if len(steps) > max_steps:
                break
            if steps[-1] == 0:
                return net

        logger.error(
            "Could not generate connected network with given "
            "parameters. Try removing and/or modifying some of "
            "them."
        )

    def generate_neigborhood_network(self) -> "RangeNetworkType":
        """
        Generates a network where all nodes are in one hop neighborhood of
        at least one node.

        Finds out the node in the middle, which is the node with the minimum maximum
        distance to all other nodes, and sets that distance as the new commRange.

        This generator ignores all other parameters except comm_range and n counts.

        :return: The generated network.
        :rtype: RangeNetworkType
        """
        net = self._create_modify_network()

        max_distances = []
        for node in net:
            distances = [sqrt(sum((net.pos[node] - net.pos[neighbor]) ** 2)) for neighbor in net]
            max_distances.append(max(distances))
        min_distance = min(max_distances)
        for node in net:
            node.commRange = min_distance + 1
        return net

    def generate_homogeneous_network(self, randomness=0.11) -> Optional["RangeNetworkType"]:
        """
        Generates a network where nodes are located approximately homogeneous.

        :param randomness: Controls random perturbation of the nodes. It is given as a part of the environment size.
        :type randomness: float

        :return: The generated random network.
        :rtype: RangeNetworkType
        """
        net = self._create_modify_network()
        n = len(net)
        h, w = net.environment.image.shape
        assert net.environment.dim == 2  # works only for 2d environments
        size = w

        positions = generate_mesh_positions(net.environment, n)
        for i in range(n):
            pos = array([-1, -1])  # some non space point
            while not net.environment.is_space(pos):
                pos = positions[i, :n] + (rand(2) - 0.5) * (size * randomness)
            net.pos[net.nodes_sorted()[i]] = pos

        if isinstance(net, RangeNetwork):
            net.recalculate_edges()
        # TODO: this is not intuitive but generate_random network with net
        # given as argument will check if conditions are satisfied and act
        # accordingly, to change only commRange set limits to number of nodes
        self.n_count = self.n_max = self.n_min = n
        return self.generate_random_network(net)

    @staticmethod
    def __get_ring_pos(n: int, env: "Environment2D") -> list[tuple[float, float]]:
        """
        A helper method for generating positions of nodes on a circle.

        :param n: The number of nodes.
        :type n: int
        :param env: The environment object.
        :type env: Environment2D
        :return: The list of positions.
        :rtype: list[tuple[int, int]]
        """

        env_shape = env.image.shape
        center = (env_shape[0] // 2, env_shape[1] // 2)
        radius = 0.82 * (min(env_shape) / 2)  # 82% of the smallest dimension, leaves enough space for the node labels.

        nodes = []
        for i in range(n):
            angle = 2 * i * pi / n
            x = center[0] + radius * cos(angle)
            y = center[1] + radius * sin(angle)
            nodes.append((x, y))
        return nodes

    @classmethod
    def generate_complete_network(cls, n: int, network_type: type[T] = None, directed_network: bool = None) -> T:
        """
        Generate a complete network with n nodes. The nodes are placed on a circle.


        Examples:

        .. code-block:: python

            >>> net1 = NetworkGenerator.generate_complete_network(5)
            <BidirectionalNetwork object with 5 nodes and 10 edges>
            >>> net2 = NetworkGenerator.generate_complete_network(5, directed_network=True)
            <Network object with 5 nodes and 20 edges>
            >>> net3 = NetworkGenerator.generate_complete_network(5, network_type=BidirectionalNetwork)
            <BidirectionalNetwork object with 5 nodes and 10 edges>

        DO NOT instantiate the class, this is a class method.

        :param n: The number of nodes in the network.
        :type n: int
        :param network_type: The type of network to generate.
        :type network_type: type[NetworkType]
        :param directed_network: Only if True, the network is directed.
        :type directed_network: bool
        :return: The generated network.
        :rtype: NetworkType
        """
        if directed_network is None:
            directed_network = False

        if network_type is None:
            network_type = Network if directed_network else BidirectionalNetwork

        net = network_type()
        node_pos_list = cls.__get_ring_pos(n, net.environment)
        nodes = [net.add_node(pos=node_pos_list) for node_pos_list in node_pos_list]

        for i, j in product(range(n), range(n)):
            if i != j:
                net.add_edge(nodes[i], nodes[j])

        return net

    @classmethod
    def generate_ring_network(cls, n: int, network_type: type[T] = None, directed_network: bool = None) -> T:
        """
        Generate a ring network with n nodes. The nodes are placed on a circle.
        If network_type is a directed type, the links between the nodes are one-way only so the network is fully
        connected.


        Example:

        .. code-block:: python

            >>> net = NetworkGenerator.generate_ring_network(6)
            <BidirectionalNetwork object with 6 nodes and 6 edges>
            >>> net = NetworkGenerator.generate_ring_network(6, directed_network=False)
            <Network object with 6 nodes and 6 edges>

        DO NOT instantiate the class, this is a class method.

        :param n: The number of nodes in the network.
        :type n: int
        :param network_type: The type of network to generate.
        :type network_type: type[NetworkType]
        :param directed_network: Only if True, the network is directed.
        :type directed_network: bool
        :return: The generated network.
        :rtype: NetworkType
        """
        if directed_network is None:
            directed_network = False

        if network_type is None:
            network_type = Network if directed_network else BidirectionalNetwork

        net = network_type()
        node_pos_list = cls.__get_ring_pos(n, net.environment)
        nodes = [net.add_node(pos=node_pos_list) for node_pos_list in node_pos_list]

        for i in range(n):
            if i != (i + 1) % n:
                net.add_edge(nodes[i], nodes[(i + 1) % n])

        return net

    @classmethod
    def generate_star_network(cls, n: int, network_type: type[T] = None, directed_network: bool = None) -> T:
        """
        Generate a star network with n nodes. The nodes are placed on a circle with one node in the center.
        If network_type is a directed type, the links are only from the center node to the other nodes.


        Example:

        .. code-block:: python

            >>> net = NetworkGenerator.generate_star_network(5)

        DO NOT instantiate the class, this is a class method.

        :param n: The number of nodes in the network.
        :type n: int
        :param network_type: The type of network to generate.
        :type network_type: type[NetworkType]
        :param directed_network: Only if True, the network is directed.
        :type directed_network: bool
        :return: The generated network.
        :rtype: NetworkType
        """
        if n <= 1:
            raise ValueError("Star network requires at least 2 nodes.")

        if directed_network is None:
            directed_network = False

        if network_type is None:
            network_type = Network if directed_network else BidirectionalNetwork

        net = network_type()
        node_pos_list = cls.__get_ring_pos(n - 1, net.environment)

        center = (
            net.environment.image.shape[0] / 2,
            net.environment.image.shape[1] / 2,
        )

        center_node = net.add_node(pos=center)

        for i in range(n - 1):
            node = net.add_node(pos=node_pos_list[i])
            net.add_edge(center_node, node)

        return net

    @staticmethod
    def generate_hypercube_network(
        n: int | None = None,
        dimension: int | None = None,
        use_binary_labels: bool = True,
        network_type: type[T] = None,
        directed_network: bool = None,
    ) -> T:
        """
        Generate a hypercube network of the given dimension (or node count). The nodes are placed in a hypercube
        structure.


        Examples:

        .. code-block:: python

            >>> net = NetworkGenerator.generate_hypercube_network(dimension=3)
            <BidirectionalNetwork object with 8 nodes and 12 edges>
            >>> net2 = NetworkGenerator.generate_hypercube_network(dimension=3, directed_network=True)
            <Network object with 8 nodes and 24 edges>
            >>> net3 = NetworkGenerator.generate_complete_network(n=8)
            <BidirectionalNetwork object with 8 nodes and 12 edges>

        DO NOT instantiate the class, this is a class method.

        :param n: The number of nodes in the network. If None, the dimension parameter must be set.
        :type n: int
        :param dimension: The dimension of the hypercube. If None, the n parameter must be set.
        :type dimension: int
        :param network_type: The type of network to generate.
        :type network_type: type[NetworkType]
        :param directed_network: Only if True, the network is directed.
        :type directed_network: bool
        :return: The generated network.
        :rtype: NetworkType
        """
        if n is None and dimension is None:
            raise ValueError("Either the number of nodes or the dimension of the hypercube must be set.")
        if n is not None and dimension is not None:
            raise ValueError("Only one of the number of nodes or the dimension of the hypercube can be set.")
        if n is not None:
            dimension = int(log2(n))
            if 2**dimension != n:
                raise ValueError("The number of nodes must be a power of 2.")

        if directed_network is None:
            directed_network = False

        if network_type is None:
            network_type = Network if directed_network else BidirectionalNetwork

        LABEL_KEY = "HYPERCUBE_LABEL"

        def create_hypercube(dim):
            # Recursive function to create the hypercube
            # A hypercube of dimension n is the disjoint union of two hypercubes of dimension n-1, forming a perfect
            # matching between the nodes of the two hypercubes.
            node_pos = OrderedDict()
            edges = []
            dist = 1

            if dim == 0:
                node = Node()
                node.memory[LABEL_KEY] = "0"
                node_pos[node] = (0, 0)
            elif dim == 1:
                node1 = Node()
                node1.memory[LABEL_KEY] = "0"
                node2 = Node()
                node2.memory[LABEL_KEY] = "1"
                node_pos[node1] = (0, 0)
                node_pos[node2] = (dist, 0)
                edges.append((node1, node2))
            else:
                part_1_nodes, part_1_edges = create_hypercube(dim - 1)
                part_2_nodes, part_2_edges = create_hypercube(dim - 1)

                edges += part_1_edges
                edges += part_2_edges

                part_1_width = max([pos[0] for pos in part_1_nodes.values()])
                part_1_height = max([pos[1] for pos in part_1_nodes.values()])

                if dim == 1:  # Grow only in the x-axis
                    x_offset = dist
                    y_offset = 0
                elif dim == 2:  # Grow only in the y-axis
                    x_offset = 0
                    y_offset = dist
                elif dim == 3:  # Grow equally in both axes
                    x_offset = dist / 2
                    y_offset = dist / 2
                elif dim % 2 == 0:  # Even dimensions grow in the x-axis
                    x_offset = part_1_width * 1.1
                    y_offset = dist / 4
                else:  # Odd dimensions grow in the y-axis
                    x_offset = dist / 4
                    y_offset = part_1_height * 1.1

                for node, pos in part_1_nodes.items():
                    node_pos[node] = pos
                    node.memory[LABEL_KEY] = "0" + node.memory[LABEL_KEY]
                for node, pos in part_2_nodes.items():
                    node_pos[node] = (pos[0] + x_offset, pos[1] + y_offset)
                    node.memory[LABEL_KEY] = "1" + node.memory[LABEL_KEY]

                for node1, node2 in zip(part_1_nodes.keys(), part_2_nodes.keys()):
                    edges.append((node1, node2))

            return node_pos, edges

        # Create the nodes
        node_pos_list, edges = create_hypercube(dimension)

        # Create the network
        net = network_type()
        canvas_shape = net.environment.image.shape
        usable_shape = (canvas_shape[1] * 0.82, canvas_shape[0] * 0.82)

        # Normalize the positions
        max_x = max(max([pos[0] for pos in node_pos_list.values()]), 1)
        max_y = max(max([pos[1] for pos in node_pos_list.values()]), 1)

        for node, pos in node_pos_list.items():
            # If the dimension is 0 or 1, the nodes are in the center
            x = pos[0] if dimension != 0 else 0.5
            y = pos[1] if dimension not in (0, 1) else 0.5
            final_pos = (x / max_x * usable_shape[0], y / max_y * usable_shape[1])

            # Add the node
            net.add_node(node, pos=final_pos)
            if use_binary_labels:
                net.labels[node] = node.memory[LABEL_KEY]

            # Remove the label from the memory as it represents some knowledge of the network
            del node.memory[LABEL_KEY]

        # Add the edges to the network
        for node1, node2 in edges:
            net.add_edge(node1, node2)
            if net.is_directed():
                net.add_edge(node2, node1)

        return net

    @classmethod
    def generate_mesh_network(
        cls,
        n: int = None,
        a: int = None,
        b: int = None,
        torus: bool = False,
        network_type: type[T] = None,
        directed_network: bool = None,
    ) -> T:
        """
        Generate a mesh (or torus) network with n nodes (or a x b nodes).
        If network_type is a directed type, the links are only north and east. Only with torus, this gives a fully
        connected network nonetheless.


        Example:

        .. code-block:: python

            >>> net = NetworkGenerator.generate_mesh_network(a=4, b=7)

        DO NOT instantiate the class, this is a class method.

        :param n: The number of nodes in the mesh/torus network. Optional.
        :type n: int
        :param a: Width of the mesh/torus. Optional.
        :type a: int
        :param b: Height of the mesh/torus. Optional.
        :type b: int
        :param torus: Whether or not to add "returning" edges.
        :type torus: bool
        :param network_type: The type of network to generate.
        :type network_type: type[NetworkType]
        :param directed_network: Only if True, the network is directed.
        :type directed_network: bool
        :return: The generated network.
        :rtype: NetworkType
        """
        if directed_network is None:
            directed_network = False

        if network_type is None:
            network_type = Network if directed_network else BidirectionalNetwork

        if a is None or b is None:
            if n is None:
                raise ValueError("Mesh network generator needs (a, b) or n.")
            if int(sqrt(n)) != sqrt(n):
                raise ValueError("Value n given must be a perfect square.")

            a = b = int(sqrt(n))

        node_pos_list = {(i, j): Node() for i in range(a) for j in range(b)}

        net = network_type()
        canvas_shape = net.environment.image.shape
        usable_shape = (canvas_shape[1] * 0.82, canvas_shape[0] * 0.82)
        bottom_margin = (
            canvas_shape[1] * (1 - 0.83) / 4,
            canvas_shape[0] * (1 - 0.83) / 4,
        )

        # Normalize the positions
        max_x = max(max([pos[0] for pos in node_pos_list.keys()]), 1)
        max_y = max(max([pos[1] for pos in node_pos_list.keys()]), 1)

        for (x, y), node in node_pos_list.items():
            # If the dimension is 0 or 1, the nodes are in the center
            final_pos = (
                x / max_x * usable_shape[0] + bottom_margin[0],
                y / max_y * usable_shape[1] + bottom_margin[1],
            )
            net.add_node(node, pos=final_pos)

        for (x, y), node in node_pos_list.items():
            north_and_east_neighbors = [(x, y + 1), (x + 1, y)] if not torus else [(x, (y + 1) % b), ((x + 1) % a, y)]
            for pos_neigh in north_and_east_neighbors:
                if pos_neigh in node_pos_list:
                    net.add_edge(node, node_pos_list[pos_neigh])

        return net

    generate_grid_network = generate_mesh_network


def generate_mesh_positions(env, n):
    """
    Generate mesh positions for the given environment and number of intersections.

    :param env: The environment object.
    :type env: Environment
    :param n: The desired number of intersections.
    :type n: int
    :return: An array of mesh positions.
    :rtype: numpy.ndarray
    """
    h, w = env.image.shape
    # initial d
    d = sqrt(h * w / n)

    def get_mesh_pos(d, dx, dy, w, h):
        return [
            (xi_yi[0] * d + dx, xi_yi[1] * d + dy)
            for xi_yi in product(list(range(int(round(w / d)))), list(range(int(round(h / d)))))
        ]

    n_mesh = 0
    direction = []
    while True:
        n_mesh = len([1 for pos in get_mesh_pos(d, 0.5 * d, 0.5 * d, w, h) if env.is_space(pos)])
        direction.append(sign(n - n_mesh))
        if n_mesh == n or (len(direction) >= 10 and abs(sum(direction[-3:])) < 3 and n_mesh > n):
            break
        d *= sqrt(n_mesh / float(n))
    return array(tuple(pos for pos in get_mesh_pos(d, 0.5 * d, 0.5 * d, w, h) if env.is_space(pos)))
    # TODO: n_mesh could be brought closer to n with modification of dx and dy
    # dx = 0.5*d
    # dy = 0.5*d


class NetworkGeneratorException(Exception):
    pass
