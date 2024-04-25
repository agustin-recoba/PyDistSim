from enum import StrEnum


class Restrictions(StrEnum):
    BidirectionalLinks = "BidirectionalLinks"
    TotalReliability = "TotalReliability"
    Connectivity = "Connectivity"
    UniqueInitiator = "UniqueInitiator"