from typing import TYPE_CHECKING

from pydistsim.algorithm.node_algorithm import (
    NeighborLabel,
    NodeAccess,
    NodeAlgorithm,
    StatusValues,
)
from pydistsim.message import Message
from pydistsim.restrictions.communication import BidirectionalLinks
from pydistsim.restrictions.reliability import TotalReliability
from pydistsim.restrictions.topological import Connectivity, UniqueInitiator

if TYPE_CHECKING:
    from pydistsim.network import Node


class Flood(NodeAlgorithm):
    required_params = ("informationKey",)

    class Status(StatusValues):
        INITIATOR = "INITIATOR"
        IDLE = "IDLE"
        DONE = "DONE"

    S_init = (Status.INITIATOR, Status.IDLE)
    S_term = (Status.DONE,)

    restrictions = (
        BidirectionalLinks,
        TotalReliability,
        Connectivity,
        UniqueInitiator,
    )

    def initializer(self):
        ini_nodes: list["Node"] = []
        for node in self.network.nodes():
            node.status = self.Status.IDLE
            if self.informationKey in node.memory:
                node.status = self.Status.INITIATOR
                ini_nodes.append(node)
        for ini_node in ini_nodes:
            ini_node.push_to_inbox(Message(meta_header=NodeAlgorithm.INI, destination=ini_node))

    @Status.INITIATOR
    def spontaneously(self, node: NodeAccess, message: Message):
        self.send(
            node,
            Message(
                header="Information",
                data=node.memory[self.informationKey],
                destination=list(node.neighbors()),
            ),
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
                    Message(
                        destination=destination_nodes,
                        header="Information",
                        data=message.data,
                    ),
                )
        node.status = self.Status.DONE

    @Status.DONE
    def default(self, *args, **kwargs):
        "Do nothing, for all inputs."
        pass
