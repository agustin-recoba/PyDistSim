############
Installation
############

This document assumes you are familiar with using command prompt or shell. It should outline the necessary steps to install software needed for using PyDistSim.

************
Requirements
************

* `Python`_ 3.11
* `Setuptools`_
* `NumPy`_
* `SciPy`_
* `Matplotlib`_
* `PySide6`_ (for gui)
* `IPython`_
* `NetworkX`_
* `PyPNG`_

.. _Python: http://www.python.org
.. _Setuptools: http://pypi.python.org/pypi/setuptools
.. _NumPy: http://numpy.scipy.org
.. _SciPy: http://www.scipy.org
.. _Matplotlib: http://matplotlib.org/
.. _PySide6: http://qt-project.org/wiki/PySide
.. _IPython: http://ipython.org/
.. _NetworkX: http://networkx.lanl.gov/
.. _PyPNG: https://github.com/drj11/pypng

If you don't have all required packages already installed and/or want them installed in an isolated environment (see note below) please follow the instructions for your OS in the following sections.

.. _discourage-systemwide:

..  note::

    Since there can be only one version of any package installed system-wide in some cases this can result in situation where two programs need different versions of the same package. This is resolved by using isolated virtual environments.

.. figure:: _images/virtualenv_system.png
   :align: center

   Virtual environments *live* in a separate directories and they are independent form system-wide Python installation.

Alternatively, if none of the above is your concern, although not recommended, all required packages can be installed system-wide using their respective instructions for appropriate OS and then PyDistSim can be installed by using::

    $ pip install pydistsim


*******
Windows
*******

Windows version should be as simple as installing `Python 3.11 for windows <https://www.python.org/downloads/release/python-3110/>`_ and running ``pip install pydistsim``.

*****************************
Linux (Debian/Ubuntu based)
*****************************

To install Python 3.11, run::

    $ sudo apt install python3.11

Depending of the flavour of linux, some packages are required for getting and compiling the source::

    $ sudo apt-get install libxkbcommon-x11-0 libegl1 opencv-python-headless libgl1-mesa-glx

**********
Virtualenv
**********

pip and virtualenv (venv) are included in Python 3.11. To create a new virtual environment run::

    $ python3.11 -m venv pydistsim_env

.. _linux-venvact:

Activate virtual environment on Linux::

    $ source pydistsim_env/bin/activate

.. _windows-venvact:

Activate virtual environment on Windows::

    $ pydistsim_env\Scripts\activate


*********
PyDistSim
*********

Finally, in order to download and install PyDistSim and all other required packages there are two available options, use one of them:

#. *Stable*: for latest stable version use package from PyPI::

    (pydistsim_env)> pip install pydistsim

#. *Development*: to install latest development version of the PyDistSim use source from github repo::

    (pydistsim_env)> pip install -e git+https://github.com/agustin-recoba/PyDistSim#egg=PyDistSim

Starting PyDistSim
==================

Before starting, make sure that virtual environment is :ref:`activated <linux-venvact>` and run ``ipydistsim`` for interactive console or ``pydistsim-simgui`` for simulation GUI. For more details refer to :doc:`starting`.

.. _virtualenv: http://www.virtualenv.org/
