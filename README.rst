PyDistSim
=========

|travis| |readthedocs| |codefactor| |coveralls|

.. |travis| image:: https://app.travis-ci.com/agustin-recoba/pydistsim.svg?token=zk1hY6ZALwZTY3bjX2Aq&branch=main
    :target: https://app.travis-ci.com/agustin-recoba/pydistsim
    :alt: Build Status
.. |coveralls| image:: https://coveralls.io/repos/github/agustin-recoba/PyDistSim/badge.svg?branch=main
    :target: https://coveralls.io/github/agustin-recoba/PyDistSim?branch=main
    :alt: Coverage Status
.. |readthedocs| image:: https://readthedocs.org/projects/pydistsim/badge/?version=main
    :target: https://pydistsim.readthedocs.io/?badge=main
    :alt: Documentation Status
.. |codefactor| image:: https://www.codefactor.io/repository/github/agustin-recoba/pydistsim/badge
   :target: https://www.codefactor.io/repository/github/agustin-recoba/pydistsim
   :alt: CodeFactor


PyDistSim is a Python package for event-based simulation and evaluation of distributed algorithms. It is a fork of the
deprecated `Pymote <https://github.com/darbula/pymote>`_.

This fork aims at providing new features, redesigned APIs and better documentation. It is being developed by Agustin
Recoba in the context of his grade thesis at `Facultad de Ingeniería, Universidad de la República <https://www.fing.edu.uy/>`_.

Definition of the distributed environment, entities and actions used for making PyDistSim are taken mainly from
`Design and Analysis of Distributed Algorithms <http://eu.wiley.com/WileyCDA/WileyTitle/productCd-0471719978,descCd-description.html>`_
by Nicola Santoro.

PyDistSim's main goal is to provide a framework for fast implementation, easy simulation and data-driven algorithmic
analysis of distributed algorithms.

Currently, PyDistSim supports IPython console or Jupyter notebooks. The gui is still in development and is not recommended
for any type of use.

.. image:: https://raw.githubusercontent.com/agustin-recoba/PyDistSim/main/docs/install/_images/pydistsim_console_gui.png
   :align: center
   :alt: PyDistSim console and gui

\

PyDistSim is being developed on top of `NetworkX <https://github.com/networkx/networkx/>`_ and is meant to be used along other scientific packages such as SciPy, NumPy and matplotlib. Currently, gui runs on PySide (Qt bindings) and console is jazzy IPython.

Installation
------------

For installation instructions please visit `the documentation <https://pydistsim.readthedocs.io/install/installation.html>`_.

Literature
----------

Santoro, N.: *Design and Analysis of Distributed Algorithms*, `2006 <http://eu.wiley.com/WileyCDA/WileyTitle/productCd-0471719978,descCd-description.html>`_

Arbula, D. and Lenac, K.: *Pymote: High Level Python Library for Event-Based Simulation and Evaluation of Distributed Algorithms*, International Journal of Distributed Sensor Networks, Volume `2013 <https://journals.sagepub.com/doi/10.1155/2013/797354>`_

Recoba, A: *PyDistSim: Framework de simulación de algoritmos distribuidos en redes en Python*, 2024
