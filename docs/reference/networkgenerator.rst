.. _networkgenerator:

#################
Network Generator
#################

Implementation of different methods for automated network creation.
It defines parameters (conditions) that generated network must satisfy.

It works in two modes:

#. Instanced generation
#. Static generation


Static generation is used for quick network generation without any additional conditions. It is appropriately
exemplified in `the network generation notebook`_.

.. _the network generation notebook: ../notebooks/network_generators.ipynb


Continue reading this document for a explanation of instanced generation.


**************
Class overview
**************

.. currentmodule:: pydistsim.network.generator
.. automodule:: pydistsim.network.generator
.. autoclass:: NetworkGenerator

*******
Methods
*******

.. automethod:: pydistsim.network.generator.NetworkGenerator.generate_random_network
.. automethod:: pydistsim.network.generator.NetworkGenerator.generate_neigborhood_network

**************************************************
Default procedure for instanced network generation
**************************************************

For any generator *instance* method network attributes take default priorities
which are defined like this:

1. first network is created in given environment with `n_count` number
   of nodes and `comm_range` communication range

2. if `connected` is True it must be satisfied, if not satisfied initially:
  * gradually increase number of nodes up to `n_max`
  * if comm_range is None gradually increase nodes commRange
  * if still not connected raise an exception
3. if `degree` condition is defined and current network degree is
  * lower - repeat measures from the last step to increase current
    network degree
  * higher one degree or more - try countermeasures i.e. decrease number of
    nodes and commRange but without influencing other defined and already
    satisfied parameters (`connected`)

The generated network is returned as a :class:`pydistsim.network.rangenetwork.RangeNetwork` or :class:`pydistsim.network.rangenetwork.BidirectionalRangeNetwork` object.
