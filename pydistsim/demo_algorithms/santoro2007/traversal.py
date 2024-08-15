from pydistsim.algorithm import NodeAlgorithm, StatusValues
from pydistsim.message import Message
from pydistsim.restrictions.communication import BidirectionalLinks
from pydistsim.restrictions.reliability import TotalReliability
from pydistsim.restrictions.topological import Connectivity, UniqueInitiator


class DFT(NodeAlgorithm):
    required_params = ()
    default_params = {"visitedAction": lambda node: None}

    class Status(StatusValues):
        INITIATOR = "INITIATOR"
        IDLE = "IDLE"
        DONE = "DONE"
        VISITED = "VISITED"

    S_init = (Status.INITIATOR, Status.IDLE)
    S_term = Status.DONE

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
        ini_node.status = self.Status.INITIATOR
        ini_node.push_to_inbox(Message(meta_header=NodeAlgorithm.INI, destination=ini_node))

    @Status.INITIATOR
    def spontaneously(self, node, message):
        node.memory["parent"] = None
        node.memory["unvisited"] = list(node.neighbors())
        self.visitedAction(node)
        self.visit(node)

    @Status.INITIATOR
    def default(self, node, message):
        raise Exception("Dont disturb intitator!")

    @Status.IDLE
    def receiving(self, node, message):
        if message.header == "Token":
            node.memory["parent"] = message.source
            node.memory["unvisited"] = list(node.neighbors())
            node.memory["unvisited"].remove(node.memory["parent"])
            self.visitedAction(node)
            self.visit(node)
        else:
            raise Exception("Should not be here.")

    @Status.VISITED
    def receiving(self, node, message):
        if message.header == "Token":
            node.memory["unvisited"].remove(message.source)
            self.send_msg(node, Message(header="Backedge", destination=message.source))
        elif message.header == "Return":
            self.visit(node)
        elif message.header == "Backedge":
            self.visit(node)

    @Status.DONE
    def default(self, node, message):
        raise Exception("Im done!!!")

    def visit(self, node):
        if len(node.memory["unvisited"]) == 0:
            if node.memory["parent"] is not None:
                self.send_msg(node, Message(header="Return", destination=node.memory["parent"]))
            node.status = self.Status.DONE
        else:
            next_unvisited = node.memory["unvisited"].pop()
            self.send_msg(node, Message(header="Token", destination=next_unvisited))
            node.status = self.Status.VISITED


class DFStar(NodeAlgorithm):
    required_params = ()
    default_params = {"neighborsKey": "Neighbors", "visitedAction": lambda node: None}

    class Status(StatusValues):
        INITIATOR = "INITIATOR"
        IDLE = "IDLE"
        AVAILABLE = "AVAILABLE"
        VISITED = "VISITED"
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
        ini_node.status = self.Status.INITIATOR
        ini_node.push_to_inbox(Message(meta_header=NodeAlgorithm.INI, destination=ini_node))

    @Status.INITIATOR
    def spontaneously(self, node, message):
        node.memory["initiator"] = True
        node.memory["unvisited"] = list(node.neighbors())
        node.memory["next"] = node.memory["unvisited"].pop()
        if len(node.memory["unvisited"]) > 0:
            self.send_msg(
                node,
                Message(
                    header="T",
                    destination=node.memory["next"],
                ),
            )
            self.send_msg(node, Message(header="Visited", destination=node.memory["unvisited"]))
            node.status = self.Status.VISITED
            self.visitedAction(node)
        else:
            node.status = self.Status.DONE

    @Status.IDLE
    def receiving(self, node, message):
        if message.header == "T":
            node.memory["unvisited"] = list(node.neighbors())
            self.first_visit(node, message)

        if message.header == "Visited":
            node.memory["unvisited"] = list(node.neighbors())
            node.memory["unvisited"].remove(message.source)
            node.status = self.Status.AVAILABLE

    @Status.AVAILABLE
    def receiving(self, node, message):
        if message.header == "T":
            self.first_visit(node, message)

        if message.header == "Visited":
            node.memory["unvisited"].remove(message.source)

    @Status.VISITED
    def receiving(self, node, message):
        if message.header == "T":
            node.memory["unvisited"].remove(message.source)
            # late visited, should not happen in unitary communication delay
            if node.memory["next"] == message.source:
                self.visit(node, message)

        if message.header == "Visited":
            node.memory["unvisited"].remove(message.source)
            if node.memory["next"] == message.source:
                self.visit(node, message)

        if message.header == "Return":
            self.visit(node, message)

    @Status.DONE
    def default(self, node, message):
        pass

    def first_visit(self, node, message: Message):
        # TODO: initiator is redundant - it can be deduced from entry==None
        node.memory["initiator"] = False
        node.memory["entry"] = message.source
        self.visitedAction(node)
        try:
            node.memory["unvisited"].remove(message.source)
        except ValueError:
            pass
        if node.memory["unvisited"]:
            node.memory["next"] = node.memory["unvisited"].pop()
            self.send_msg(
                node,
                Message(
                    header="T",
                    destination=node.memory["next"],
                ),
            )

            self.send_msg(
                node,
                Message(
                    header="Visited",
                    destination=set(node.neighbors()) - {node.memory["entry"], node.memory["next"]},
                ),
            )
            node.status = self.Status.VISITED
        else:
            self.send_msg(node, Message(header="Return", destination=node.memory["entry"]))
            self.send_msg(
                node,
                Message(
                    header="Visited",
                    destination=set(node.neighbors()) - {node.memory["entry"]},
                ),
            )
            node.status = self.Status.DONE

    def visit(self, node, message):
        if node.memory["unvisited"]:
            node.memory["next"] = node.memory["unvisited"].pop()
            self.send_msg(
                node,
                Message(
                    header="T",
                    destination=node.memory["next"],
                ),
            )
        else:
            if not node.memory["initiator"]:
                self.send_msg(node, Message(header="Return", destination=node.memory["entry"]))
            node.status = self.Status.DONE
