.. _networkmixin:
.. currentmodule:: pydistsim.network.rangenetwork

Range Networks
=============================

PyDistSim implements an abstraction of range networks, which is a network where
each node is connected to all nodes within a certain range.
This is useful for simulating wireless networks, where the range of a node is
limited by the power of its transmitter.

For reference, see :class:`RangeNetwork` and :class:`BidirectionalRangeNetwork`.

.. inheritance-diagram:: RangeNetwork BidirectionalRangeNetwork
   :parts: 1
   :caption: Inheritance diagram for RangeNetwork and BidirectionalRangeNetwork


\


Range Types
.............................

PyDistSim implements several range types, which define the behavior of the range network.
The rage type defines which nodes are connected to each other, but use of distance is
not mandatory. For example, the :class:`CompleteRangeType` connects all nodes to all other nodes,
regardless of distance.

To add a new range type, the developer needs to implement the :class:`RangeType` interface, and
override the method :meth:`RangeType.in_comm_range`.

.. inheritance-diagram:: RangeType UdgRangeType CompleteRangeType SquareDiscRangeType
   :parts: 1
   :caption: Inheritance diagram for RangeType
