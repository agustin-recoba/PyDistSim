from pydistsim.algorithm.node_algorithm import NodeAlgorithm, StatusValues
from pydistsim.algorithm.node_wrapper import NodeAccess
from pydistsim.message import Message
from pydistsim.restrictions.communication import BidirectionalLinks
from pydistsim.restrictions.reliability import TotalReliability
from pydistsim.restrictions.topological import Connectivity, UniqueInitiator


class Flood(NodeAlgorithm):
    default_params = {
        "informationKey": "information",
        "initial_information": "Hello, world!",
    }

    class Status(StatusValues):
        INITIATOR = "INITIATOR"
        IDLE = "IDLE"
        DONE = "DONE"

    S_init = (Status.INITIATOR, Status.IDLE)
    S_term = (Status.DONE,)

    algorithm_restrictions = (
        BidirectionalLinks,
        TotalReliability,
        Connectivity,
        UniqueInitiator,
    )

    def initializer(self):
        for node in self.network.nodes():
            node.status = self.Status.IDLE

        ini_node = self.network.nodes_sorted()[0]
        ini_node.push_to_inbox(Message(meta_header=NodeAlgorithm.INI, destination=ini_node))
        ini_node.status = self.Status.INITIATOR
        ini_node.memory[self.informationKey] = self.initial_information

    @Status.INITIATOR
    def spontaneously(self, node: NodeAccess, message: Message):
        self.send(
            node,
            data=node.memory[self.informationKey],
            destination=list(node.neighbors()),
            header="Information",
        )
        node.status = self.Status.DONE

    @Status.IDLE
    def receiving(self, node: NodeAccess, message: Message):
        if message.header == "Information":
            node.memory[self.informationKey] = message.data
            destination_nodes = node.neighbors()
            # send to every neighbor, except the original sender
            destination_nodes.remove(message.source)
            if destination_nodes:
                self.send(
                    node,
                    destination=destination_nodes,
                    header="Information",
                    data=message.data,
                )
        node.status = self.Status.DONE

    @Status.DONE
    def default(self, *args, **kwargs):
        "Do nothing, for all inputs."
        pass
