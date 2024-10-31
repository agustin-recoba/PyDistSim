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
   #. How fast a node can process a message. This is used to model the case where a node can only process a certain
      number of messages per time unit.

To apply these properties to a network, simply set :attr:`NetworkType.behavioral_properties` to an instance of
:class:`NetworkBehaviorModel`.


Some predefined models are available as class attributes of the :class:`NetworkBehaviorModel` class:
   #. :attr:`NetworkBehaviorModel.IdealCommunication`
   #. :attr:`NetworkBehaviorModel.UnorderedCommunication`
   #. :attr:`NetworkBehaviorModel.ThrottledCommunication`
   #. :attr:`NetworkBehaviorModel.UnorderedThrottledCommunication`
   #. :attr:`NetworkBehaviorModel.RandomDelayCommunication`
   #. :attr:`NetworkBehaviorModel.RandomDelayCommunicationSlowNodes`
   #. :attr:`NetworkBehaviorModel.RandomDelayCommunicationVerySlowNodes`
   #. :attr:`NetworkBehaviorModel.UnorderedRandomDelayCommunication`
   #. :attr:`NetworkBehaviorModel.UnorderedRandomDelayCommunication`
   #. :attr:`NetworkBehaviorModel.UnlikelyRandomLossCommunication`

To get maximum flexibility, delay and loss are defined as functions that take the message and the network as arguments.
This means that the delay and loss can be defined as functions of the message and the network state, so this can be used
to model more complex scenarios.
