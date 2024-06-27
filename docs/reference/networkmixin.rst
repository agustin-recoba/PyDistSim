.. _networkmixin:
.. currentmodule:: pydistsim.network.network

#############################
Networks and the NetworkMixin
#############################


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
   :caption: Inheritance diagram for Network and BidirectionalNetwork

************************
Communication properties
************************
.. currentmodule:: pydistsim.network.networkbehavior

The communication properties of the network are defined in the :class:`NetworkBehaviorModel` class. This
class defines the three parameters that are used to model the communication properties of the network:

   #. Whether or not the messages being sent at a given time will arrive in the same order they were sent (massage
      ordering).
   #. The amount of delay that the messages will have when being sent.
   #. The frequency at which the messages will be lost.

To apply these properties to a network, simply set :attr:`NetworkMixin.behavioral_properties` to an instance of
:class:`NetworkBehaviorModel`.


Some predefined models are available in the :class:`ExampleProperties` class:
   #. :attr:`ExampleProperties.IdealCommunication`
   #. :attr:`ExampleProperties.UnorderedCommunication`
   #. :attr:`ExampleProperties.ThrottledCommunication`
   #. :attr:`ExampleProperties.UnorderedThrottledCommunication`
   #. :attr:`ExampleProperties.RandomDelayCommunication`
   #. :attr:`ExampleProperties.UnorderedRandomDelayCommunication`
   #. :attr:`ExampleProperties.UnorderedRandomDelayCommunication`
   #. :attr:`ExampleProperties.UnlikelyRandomLossCommunication`

To get maximum flexibility, delay and loss are defined as functions that take the message and the network as arguments.
This means that the delay and loss can be defined as functions of the message and the network state, so this can be used
to model more complex scenarios.
