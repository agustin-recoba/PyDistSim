.. _networkgenerator:

.. currentmodule:: pydistsim.network.generator


########################
Network generation intro
########################

PyDistSim comes with a battery of different methods for automated network creation.
It works in two modes:

#. Instanced generation
#. Static generation

When you use it in instance mode, you instantiate the :class:`NetworkGenerator` with the parameters you want the network to have
and on that instance you call ``generate_random_network`` or ``generate_homogeneous_network`` to return a network.
This is the most configurable way to generate random networks but without any particular structure.
Check the :class:`NetworkGenerator` class reference for more information on the parameters you can use.


On the other hand, when you use the class or static mode, you do not need to instantiate NetworkGenerator, just call
its class methods:

#. :meth:`NetworkGenerator.generate_complete_network`
#. :meth:`NetworkGenerator.generate_ring_network`
#. :meth:`NetworkGenerator.generate_star_network`
#. :meth:`NetworkGenerator.generate_hypercube_network`
#. :meth:`NetworkGenerator.generate_mesh_network`

These class methods receive a minimal configuration of parameters (in general only the number of nodes and if the
network should be directed or not).

Static generation is used for quick network generation without any additional conditions. It is appropriately
exemplified in `the network generation notebook`_.

.. _the network generation notebook: ../notebooks/network_generators.ipynb
