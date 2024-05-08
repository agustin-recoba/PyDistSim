from pydistsim.algorithm import NodeAlgorithm, StatusValues
from pydistsim.message import Message
from pydistsim.restrictions import Restrictions


class Flood(NodeAlgorithm):
    required_params = ("informationKey",)
    default_params = {"neighborsKey": "Neighbors"}

    class Status(StatusValues):
        INITIATOR = "INITIATOR"
        IDLE = "IDLE"
        DONE = "DONE"

    S_init = [Status.INITIATOR, Status.IDLE]
    S_term = [Status.DONE]

    restrictions = [
        Restrictions.BidirectionalLinks,
        Restrictions.TotalReliability,
        Restrictions.Connectivity,
        Restrictions.UniqueInitiator,
    ]

    def initializer(self):
        ini_nodes = []
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()["Neighbors"]
            node.status = self.Status.IDLE
            if self.informationKey in node.memory:
                node.status = self.Status.INITIATOR
                ini_nodes.append(node)
        for ini_node in ini_nodes:
            self.network.outbox.insert(
                0, Message(meta_header=NodeAlgorithm.INI, destination=ini_node)
            )

    @Status.INITIATOR
    def spontaneously(self, node, message):
        node.send(Message(header="Information", data=node.memory[self.informationKey]))
        node.status = self.Status.DONE

    @Status.IDLE
    def receiving(self, node, message):
        if message.header == "Information":
            node.memory[self.informationKey] = message.data
            destination_nodes = list(node.memory[self.neighborsKey])
            # send to every neighbor-sender
            destination_nodes.remove(message.source)
            if destination_nodes:
                node.send(
                    Message(
                        destination=destination_nodes,
                        header="Information",
                        data=message.data,
                    )
                )
        node.status = self.Status.DONE

    @Status.DONE
    def default(self, *args, **kwargs):
        "Do nothing, for all inputs."
        pass
