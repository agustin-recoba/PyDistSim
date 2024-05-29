from itertools import product
from typing import TYPE_CHECKING, Optional

from numpy import array, sign, sqrt
from numpy.random import rand

from pydistsim.conf import settings
from pydistsim.logger import logger
from pydistsim.network.network import Node
from pydistsim.network.rangenetwork import BidirectionalRangeNetwork, RangeNetwork

if TYPE_CHECKING:
    from pydistsim.network.rangenetwork import RangeNetworkType


class NetworkGenerator:
    """
    Class for generating networks with specified properties.
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
        directed=settings.DIRECTED,
        **kwargs,
    ):
        """
        :param n_count: int, number of nodes, if None settings.N_COUNT is used
        :param n_min: int, minimum number of nodes, if not set it is equal to n_count
        :param n_max: int, maximum number of nodes, if not set it is equal to n_count
        :param enforce_connected: bool, if True network must be fully connected
        :param degree: int, average number of neighbors per node
        :param comm_range: int, nodes communication range, if None settings.COMM_RANGE is used
            and it is a signal that this value can be changed if needed to
            satisfy other wanted properties (connected and degree)
        :param method: str, sufix of the name of the method used to generate network
        :param kwargs: network and node __init__ kwargs i.e.:
            - environment: Environment, environment in which the network should be created, if None
            settings.ENVIRONMENT is used
            - rangeType: RangeType
            - algorithms: tuple
            - commRange: int, overrides `comm_range`
            - sensors: tuple

        Basic usage:

        >>> net_gen = NetworkGenerator()
        >>> net = net_gen.generate()

        """
        self.n_count = n_count or settings.N_COUNT
        self.n_min = self.n_count if n_min is None else n_min
        self.n_max = self.n_count if n_max is None else n_max
        if self.n_count < self.n_min or self.n_count > self.n_max:
            raise NetworkGeneratorException("Number of nodes must be between n_min and n_max.")
        if degree and degree >= self.n_max:
            raise NetworkGeneratorException(
                "Degree % d must be smaller than maximum number of nodes %d." % (degree, self.n_max)
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
                    logger.debug("Added node, number of nodes: {}", len(net))
                elif not self.comm_range:
                    for node in net.nodes():
                        node.commRange += step
                    logger.debug("Increased commRange to {}", node.commRange)
                else:
                    return None
            else:
                min_node = net.nodes_sorted()[0]
                if len(net) > self.n_min and len(net) > 1:
                    net.remove_node(min_node)
                    logger.debug("Removed node, nodes left: {}", len(net))
                elif not self.comm_range:
                    for node in net:
                        node.commRange += step
                    logger.debug("Decreased commRange to {}", node.commRange)
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
        :rtype: Network
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
        :rtype: Network
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
