from typing import TYPE_CHECKING

from pydistsim.restrictions.base_restriction import CheckableRestriction

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType

from abc import ABC


class SimulationAxiom(CheckableRestriction, ABC):
    "Bases of the definition of the distributed computing environment."

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        """
        Check if the axiom is satisfied by the network.
        As the axioms are modeled in the implementation itself,
        it is not necessary to implement this method.

        :param network: The network object representing the simulation network.
        :type network: NetworkType
        :return: True if the axiom is satisfied, False otherwise.
        :rtype: bool
        """
        return True


class FiniteCommunicationDelays(SimulationAxiom):
    "In the absence of failures, communication delays are finite."


class LocalOrientation(SimulationAxiom):
    "An entity can distinguish among its in and out neighbors."
