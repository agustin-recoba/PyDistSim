.. _networkbehavior:

##################################
Behavioral properties of a network
##################################
.. currentmodule:: pydistsim.network.behavior

The communication properties of the network are defined in the :class:`NetworkBehaviorModel` class. This
class defines the three parameters that are used to model the communication properties of the network:

   #. Whether or not the messages being sent at a given time will arrive in the same order they were sent (massage
      ordering).
   #. The amount of delay that the messages will have when being sent.
   #. The frequency at which the messages will be lost.
   #. How rapidly the internal clocks of the nodes will increase.

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
