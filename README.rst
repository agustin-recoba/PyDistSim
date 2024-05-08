PyDistSim
=========

.. image:: https://app.travis-ci.com/agustin-recoba/pydistsim.svg?token=zk1hY6ZALwZTY3bjX2Aq&branch=main
    :target: https://app.travis-ci.com/agustin-recoba/pydistsim
    :alt: Build Status

.. image:: https://coveralls.io/repos/github/agustin-recoba/pydistsim/badge.svg
    :target: https://coveralls.io/github/agustin-recoba/pydistsim
    :alt: Coverage Status

.. image:: https://readthedocs.org/projects/pydistsim/badge/?version=main
    :target: https://pydistsim.readthedocs.io/?badge=main
    :alt: Documentation Status

.. image:: https://www.codefactor.io/repository/github/agustin-recoba/pydistsim/badge
   :target: https://www.codefactor.io/repository/github/agustin-recoba/pydistsim
   :alt: CodeFactor


PyDistSim is a Python package for event-based simulation and evaluation of distributed algorithms. It is a fork of the deprecated `Pymote <https://github.com/darbula/pymote>`_.

This fork aims at providing new features, redesigned APIs and better documentation. It is being developed by Agustin Recoba in the context of his grade thesis at `Facultad de Ingeniería, Universidad de la República <https://www.fing.edu.uy/>`_.

Definition of the distributed environment, entities and actions used for making PyDistSim are taken mainly from `Design and Analysis of Distributed Algorithms <http://eu.wiley.com/WileyCDA/WileyTitle/productCd-0471719978,descCd-description.html>`_ by Nicola Santoro.

PyDistSim's main goal is to provide a framework for fast implementation, easy simulation and data-driven algorithmic analysis of distributed algorithms.

.. figure::  _images/pydistsim_console_gui.png
   :align: center

\

PyDistSim is being developed on top of `NetworkX <https://github.com/networkx/networkx/>`_ and is ment to be used along other scientific packages such as SciPy, NumPy and matplotlib. Currently, gui runs on PySide (Qt bindings) and console is jazzy IPython.

Installation
------------

For installation instructions please visit `documentation <https://pydistsim.readthedocs.org>`_.

Literature
----------

Santoro, N.: *Design and Analysis of Distributed Algorithms*, 2006 `link <http://eu.wiley.com/WileyCDA/WileyTitle/productCd-0471719978,descCd-description.html>`_

Arbula, D. and Lenac, K.: *Pymote: High Level Python Library for Event-Based Simulation and Evaluation of Distributed Algorithms*, International Journal of Distributed Sensor Networks, Volume 2013 `link <https://journals.sagepub.com/doi/10.1155/2013/797354>`_

Recoba, A: *PyDistSim: Framework de simulación de algoritmos distribuidos en redes en Python*, 2024 `link <TODO AGREGAR LINK>`_
