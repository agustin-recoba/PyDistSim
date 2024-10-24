.. _tutorials:

#########
Tutorials
#########

Tutorials assume that the PyDistSim and all required packages are installed. If not, please refer to
the :doc:`../install/installation` section of this documentation.


**************************
Full explanation of topics
**************************

.. toctree::
   :maxdepth: 1

   implementing
   restrictions
   networkgenerator


**************
Demo notebooks
**************

Hello distributed world
=======================

This tutorial demonstrates a distributed version of the classic *Hello world* example.
Basic usage of the library is described in this demo, just `follow the steps`_.

.. _follow the steps: ../notebooks/hello_distributed_world.ipynb

Automatic network generation
============================

In this tutorial, we demonstrate how to generate a network automatically. Access `the network generation notebook`_.

.. _the network generation notebook: ../notebooks/network_generators.ipynb

Creating an animation of a run
==============================

Here we demonstrate how to generate an animation of a simulated algorithm in any given network.
Look at `the animation notebook`_.

.. _the animation notebook: ../notebooks/animation.ipynb

Visualize the construction of a tree
------------------------------------

This tutorial demonstrates how to visualize the construction of a tree in a distributed algorithm. Check out
`the tree construction notebook`_.

.. _the tree construction notebook: ../notebooks/tree_construction_viz.ipynb


Visualize the effect of network behavioral properties
-----------------------------------------------------

This tutorial exemplifies how to visualize the effect of network behavioral properties on a distributed algorithm.
Access `the network properties notebook`_.

.. _the network properties notebook: ../notebooks/behavior_viz.ipynb


Algorithm benchmarking
======================

This tutorial demonstrates how to benchmark a distributed algorithm. Access `the benchmarking notebook`_.

.. _the benchmarking notebook: ../notebooks/benchmarking.ipynb

Custom algorithm observers
==========================

This tutorial covers how to implement a observable algorithm and its corresponding observer.
Access `the notebook here`_.

.. _the notebook here: ../notebooks/custom_observer.ipynb


Ultimate example: Mega-Merger implementation and analysis
=========================================================

Check out `Mega-Merger implementation`_ and the notebooks:

#. `Animation notebooks`_.
#. `Analysis notebook`_.
#. `Testing notebook`_.


.. _Mega-Merger implementation: ../_modules/pydistsim/demo_algorithms/santoro2007/mega_merger/algorithm.html#MegaMergerAlgorithm

.. _Analysis notebook: ../notebooks/mega_merger/benchmarking.ipynb
.. _Animation notebooks: ../notebooks/mega_merger/animations.ipynb
.. _Testing notebook: ../notebooks/mega_merger/tests.ipynb



Build date: |today|


Release version: |release|
