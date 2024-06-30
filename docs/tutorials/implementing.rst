.. _implementing:

.. currentmodule:: pydistsim.algorithm.node_algorithm

####################################
Implementing a distributed algorithm
####################################

In order to implement a distributed algorithm, the class must fulfill these requirements:
    1.  It must be a subclass of :class:`NodeAlgorithm` class.
    2.  It should have a class attribute :attr:`NodeAlgorithm.Status` which is an
        enumeration of the possible states of the node. This enumeration must subclass :class:`StatusValues`.
    3.  Action implementations must be methods of the class, they must be called as the action itself and must be
        decorated with a member of the Status enumeration. One such implementation should look like this:

.. code-block:: python

    @Status.IDLE
    def receive(self, node, message):
        ...

.. note::
    To help the programmer, there is a special action :attr:`Actions.default` which will be called if the action was
    not implemented for a given status.

.. warning::
    Actions without an implementation will only log a warning message, so for no-ops, it is not necessary to implement
    anything.

*************************
"The Santoro's interface"
*************************

Send a message
==============
The :meth:`NodeAlgorithm.send` method receives a source node and a message. The message will be sent to the destinations
specified in the message itself. The destinations must be a list of nodes or a single node. The message will be sent to
all the destinations.

Set an alarm
============
The :meth:`NodeAlgorithm.set_alarm` method receives a node and a time. An empty message will be sent to the node after
the time has passed. The time is in algorithm steps, which behavior varies according to the algorithm and the simulation\
parameters.


Check the extended interface methods for advanced use of the alarm mechanism.

*******************************************
Helper functions and the extended interface
*******************************************

Alarm management
================

The :meth:`NodeAlgorithm.set_alarm` method receives an extra, optional, parameter, the message. This message will be
sent to the node when the alarm goes off. The message must be an instance of :class:`Message`. This, however, is not
meant to be used to send messages to other nodes, but to the node itself.

.. note::
    To schedule a message to be sent to another node, we recommend using the :meth:`NodeAlgorithm.send` method inside
    the callback of the alarm.

The :meth:`NodeAlgorithm.set_alarm` method returns an object that represents the alarm. This object can be used to
disable the alarm, update the time, check the time left for the alarm to go off and check if the alarm is active.


To disable alarms, the following methods are available:

    *   :meth:`NodeAlgorithm.disable_all_node_alarms` which disables all alarms of the node.
    *   :meth:`NodeAlgorithm.disable_alarm` which disables a specific alarm. The argument is the alarm object itself,
        which is returned by the :meth:`NodeAlgorithm.set_alarm` method.

And finally, to add or subtract time from a pending alarm, :meth:`NodeAlgorithm.update_alarm_time` can be used. The
arguments are the alarm object and the time to be added or subtracted. If the time subtracted is greater than the time
left for the alarm to go off, the alarm will be triggered the next "alarm triggering event" (usually the next step of
the algorithm).
