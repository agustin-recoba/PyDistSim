.. _tut_restrictions:

.. currentmodule:: pydistsim.algorithm.node_algorithm

################################################
Specifying network restrictions for an algorithm
################################################

In order to declare restrictions for a distributed algorithm, the developer must define the class attribute
:attr:`NodeAlgorithm.algorithm_restrictions` as a list or tuple of restriction types. Such types must be subclasses of
:class:`pydistsim.restrictions.base_restriction.Restriction`.

For example, for a broadcast algorithm, the restrictions could be:

.. code-block:: python

    algorithm_restrictions = (
        BidirectionalLinks,
        TotalReliability,
        Connectivity,
        UniqueInitiator,
    )

.. seealso::
    For the simulation to enforce the restrictions during runtime, the attribute :attr:`check_restrictions` of
    :class:`pydistsim.simulation.Simulation` must be set to `True`.


For a full example of a broadcast algorithm with restrictions, please refer to the file
:file:`pydistsim/demo_algorithms/broadcast.py` in the source code.


.. note::
    For the full list of available restrictions, please refer to the module reference of :mod:`pydistsim.restrictions`
    in this documentation.

.. warning::
    Some of the implemented restrictions require the algorithm to take action in the algorithm initialization.
    For example, the :class:`pydistsim.restrictions.topological.UniqueInitiator` restriction requires the algorithm to
    set the initiator node.
