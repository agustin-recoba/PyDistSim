.. _implementing:

.. currentmodule:: pydistsim.algorithm.node_algorithm

Implementing a distributed algorithm
====================================

In order to implement a distributed algorithm, the class must fulfill these requirements:
    1.  It must be a subclass of :class:`NodeAlgorithm` class.
    2.  It should have a class attribute :attr:`NodeAlgorithm.Status` which is an
        enumeration of the possible states of the node. This enumeration must subclass :class:`StatusValues`.
    3.  Action implementations must be methods of the class, they must be called as the action itself and must be
        decorated with a member of the Status enumeration. One such Implementation should look like this:

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

"The Santoro's interface"
-------------------------




Helper functions and the extended interface
-------------------------------------------
