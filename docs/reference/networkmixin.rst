.. _networkmixin:
.. currentmodule:: pydistsim.network.network

Networks and the NetworkMixin
=============================

PyDistSim uses the library :mod:`networkx` to represent graphs. :mod:`networkx` provides a rich set of graph classes and methods to work with graphs.

In order to extend the defined :class:`networkx.Graph` and :class:`networkx.DiGraph` in :mod:`networkx`, PyDistSim uses a mixin class.

This mixin class is called NetworkMixin and is defined in the network module.
For the development of the framework, we have used this mixin to define :class:`Network` and :class:`BidirectionalNetwork`,
which are subclasses of :class:`networkx.Graph` and :class:`networkx.DiGraph` respectively.

In broad terms, these NetworkMixin subclasses are responsible for the following:

* Managing the nodes and edges of the graph.
* Managing the data associated with the nodes and edges.
* Managing the network properties.
* Managing the algorithms that can be applied to the network, its state and the data associated with it.

For class and method documentation refer to :class:`NetworkMixin`.

.. inheritance-diagram:: Network BidirectionalNetwork
   :parts: 3
   :caption: Inheritance diagram for Network and BidirectionalNetwork
