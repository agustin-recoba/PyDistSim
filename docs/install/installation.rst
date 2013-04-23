Installation
############
This document assumes you are familiar with Python and using command prompt or shell. It should 
outline the necessary steps to install software needed for using Pymote.

Requirements
************
    
* `Python`_ 2.7
* `Setuptools`_ 
* `NumPy`_
* `SciPy`_
* `Matplotlib`_
* `PySide`_ (for gui)
* `IPython`_ 0.13.1
* `NetworkX`_
* `PyPNG`_ 

.. _Python: http://www.python.org
.. _Setuptools: http://pypi.python.org/pypi/setuptools
.. _NumPy: http://numpy.scipy.org
.. _SciPy: http://www.scipy.org
.. _Matplotlib: http://matplotlib.org/
.. _PySide: http://qt-project.org/wiki/PySide
.. _IPython: http://ipython.org/
.. _NetworkX: http://networkx.lanl.gov/
.. _PyPNG: https://github.com/drj11/pypng

If you don't have all required packages already installed and/or want them installed in an isolated
environment (see note below) please follow the instructions for your OS in the following sections.

.. _discourage-systemwide:

..  note::
    
    Since there can be only one version of any package installed systemwide in some cases 
    this can result in situation where two programs need different versions of the
    same package. This is resolved by using isolated virtual environments.

.. figure:: _images/virtualenv_system.png
   :align: center
   
   Virtual environments *live* in a separate directories and they are independent form systemwide
   Python installation.
   
Alternatively, if none of the above is your concern all required packages can be installed 
systemwide using their respective instructions for appropriate OS and then Pymote can be installed
simply by using::

    > pip install pymote


Linux (Ubuntu)
**************

Python 2.7 should already be installed on all new releases of Linux.

Install packages required for getting and compiling the source::
    
    $ sudo apt-get install git libatlas-dev libpng12-dev libfreetype6 libfreetype6-dev g++ libzmq-dev liblapack-dev gfortran python-dev build-essential

Virtualenv
==========

Install pip and virtualenv::
    
    $ sudo apt-get install python-pip python-virtualenv

Create virtual environment::
    
    $ virtualenv pymote_env

.. _linux-venvact:

Activate virtual environment::
    
    $ source pymote_env/bin/activate


Required packages
=================
Install required python packages into virtual environment::
    
    (pymote_env)$ pip install numpy scipy ipython matplotlib networkx pypng distribute

IPython notebook
----------------
Optionally for IPython notebook install these::

    (pymote_env)$ pip install tornado pyzmq pygments
    
PySide
------
Installing PySide into virtual environment can take some time and disk space. To avoid this, it can be installed systemwide using `these instructions <http://qt-project.org/wiki/PySide_Binaries_Linux>`_ like this::

    $ sudo add-apt-repository ppa:pyside
    $ sudo apt-get update
    $ sudo apt-get install python-pyside
    
To install it into virtual environment use these commands::

    $ sudo apt-get install cmake qt4-qmake qt-sdk
    (pymote_env)$ pip install pyside

Pymote
======
Finally, in order to download and install Pymote and all other required packages there are two
aviliable options, use one of them:

#. *Development*: to install latest development version of the Pymote use source from github repo::
    
    (pymote_env)> pip install -e git+https://github.com/darbula/pymote.git#egg=Pymote

#. *Stable*: for latest stable version use package from PyPI::
    
    (pymote_env)> pip install Pymote

For starting Pymote refer to :doc:`starting`.


Windows
*******

Install Python 2.7 using appropriate installer: `Python 2.7.3 x86 MSI Installer <http://www.python.org/ftp/python/2.7.3/python-2.7.3.msi>`_

.. warning::

    After installation append paths to ``python.exe`` (i.e. ``C:\Python27``) and path to directory 
    ``Scripts`` (i.e. ``C:\Python27\Scripts``) in the PATH 
    `environment variable <http://superuser.com/a/284351/169714>`_.


Virtualenv
==========

Instead of installing packages systemwide in these instructions we use `virtualenv`_ to create an
isolated Python environment and then install packages into this environment. This procedure is
more demanding but has the advantage of being independent from the rest of the system.

To install ``virtualenv`` first install ``distribute`` and ``pip``:

#.  download `distribute_setup.py <http://python-distribute.org/distribute_setup.py>`_
#.  download `get-pip.py <https://raw.github.com/pypa/pip/master/contrib/get-pip.py>`_
#.  enter elevated/administrator command prompt: right click on the Command prompt icon and select
    Run as administrator

        .. image:: _images/command_prompt_administrator.png
           :align: center

#.  Navigate to the directory where the files were downloaded (i.e. ``C:\Users\user\Desktop``) and
    run following commands::
    
        C:\> cd Users\user\Desktop
        C:\Users\user\Desktop> python distribute_setup.py
        C:\Users\user\Desktop> python get-pip.py

#.  After this distribute should be installed so downloaded files and temporary ``build`` directory 
    can be deleted.

#.  Install ``virtualenv``::

        C:\Users\user\Desktop> pip install virtualenv

.. note::

    When the installation of ``virtualenv`` is completed the elevated/administrator Command prompt
    is not needed anymore so it can be closed. All subsequent commands should go in the regular 
    Command prompt.

Pymote virtual environment
--------------------------

#.  To make a virtual environment in which all other packages are going to be installed first
    navigate to the directory in which you want to set up environment. This can be any directory and
    in the following steps we use ``C:\Users\user\Documents``::

        C:\Users\user> cd C:\Users\user\Documents
        C:\Users\user\Documents> virtualenv pymote_env
        New python executable in pymote_env\Scripts\python.exe
        Installing setuptools................done.
        Installing pip...................done.
    
    This command has made a new directory ``pymote_env`` inside ``C:\Users\user\Documents`` with
    separate python interpreter and two necessary packages. 

.. _windows-venvact:

#.  Activate environment::

        C:\Users\user\Documents> pymote_env\Scripts\activate
        (pymote_env) C:\Users\user\Documents>
    
    .. note::

        The ``(pymote_env)`` prefix to prompt in the last line indicates that newly created environment
        is activated. All subsequently installed packages from this modified command prompt end up in
        the activated environment. Environment can be deactivated with command ``deactivate``.

#.  Set ``PYMOTE_ENV`` environment variable as path to ``pymote_env`` directory. This way all
    executables that are not being started from the modified command prompt should know where
    to look for the environment and its packages.

    .. note::

        In Windows Vista and later use command ``setx PYMOTE_ENV "C:\path\to\pymote_env"`` to save
        environment variable permanently. In XP use the normal way through Control Panel (`instructions <http://www.microsoft.com/resources/documentation/windows/xp/all/proddocs/en-us/sysdm_advancd_environmnt_addchange_variable.mspx?mfr=true>`_).

#.  Launch text editor (use `Notepad++ <http://notepad-plus-plus.org/download>`_ or WordPad, do not
    use plain Notepad) and open ``pymote_env\Scripts\activate.bat`` file. To display the ``.bat``
    files in open dialog you have to chose All Documents (\*.\*) from the file types dropdown.

#.  Add line ``set IPYTHONDIR=%VIRTUAL_ENV%\.ipython`` *below* the line that sets ``VIRTUAL_ENV``
    environment variable, near the top. Save the document. This way IPython package which is not
    yet fully compatible with the virtualenv knows where to look for its conguration files.
  
#.  Open ``pymote_env\Scripts\deactivate.bat`` in text editor and insert line ``set IPYTHONDIR=`` 
    just below the line ``@echo off``, near the top of the document. Save the document. 

.. warning::

    After setting the environment variable and modifying ``activate.bat`` and ``deactivate.bat``
    scripts you must restart the Command prompt and reenter/reactivate ``pymote_env``. If all goes
    well commands ``echo %PYMOTE_ENV%`` and ``echo %IPYTHONDIR%`` should print environment paths.

Required packages
=================

All required packages are installed in the environment created in the previous section so before
continuing ensure that the environment is activated. Active environment is indicated with prompt 
prefix i.e. ``(pymote_env)``.

NumPy and SciPy
---------------
Since normal installation of these packages requires compiling we make a shortcut by using 
precompiled binaries and installing them into virtual environment using
`this solution <http://stackoverflow.com/a/6753898/1247955>`_:

#.  Download 
    NumPy binary `numpy-1.7.0-win32-superpack-python2.7.exe <http://sourceforge.net/projects/numpy/files/NumPy/1.7.0/numpy-1.7.0-win32-superpack-python2.7.exe/download>`_ and 
    SciPy binary `scipy-0.11.0-win32-superpack-python2.7.exe <http://sourceforge.net/projects/scipy/files/scipy/0.11.0/scipy-0.11.0-win32-superpack-python2.7.exe/download>`_.
    
    .. note::
    
        Newer versions of `NumPy <http://sourceforge.net/projects/numpy/files/NumPy/>`__ and 
        `SciPy <http://sourceforge.net/projects/scipy/files/scipy/>`__ may be available.
        

#.  Do not run downloaded ``.exe`` files as that would install them systemwide. Instead *extract* 
    them (with `7-zip <http://www.7-zip.org/download.html>`_) in some temporary
    directory i.e. ``C:\Users\user\Desktop``.

#.  Based on your processor support of `SSE <http://en.wikipedia.org/wiki/Streaming_SIMD_Extensions>`_ 
    instructions (probably sse3, see the note below) install appropriate extracted ``.exe`` files
    (nosse|sse2|sse3) using ``easy_install`` command::
    
        (pymote_env) C:\Users\user\Desktop> easy_install numpy-1.7.0-[nosse|sse2|sse3].exe
        (pymote_env) C:\Users\user\Desktop> easy_install scipy-0.11.0-[nosse|sse2|sse3].exe
    
    .. note::

        SSE3 instructions are supported by all 
        `reasonably modern processors <http://en.wikipedia.org/wiki/SSE3#CPUs_with_SSE3>`_. If 
        you're not sure try `CPU-Z <http://www.softpedia.com/get/System/System-Info/CPU-Z.shtml>`_.
        
After installation all downloaded and extracted files can be deleted.


Matplotlib
----------
Matplotlib package
is installed almost the same way as NumPy and SciPy packages in previous section using the
appropriate binary `matplotlib-1.2.0.win32-py2.7.exe <https://github.com/downloads/matplotlib/matplotlib/matplotlib-1.2.0.win32-py2.7.exe>`_.
The only difference is in the 3rd step where the extracted contents from directory 
``PLATLIB`` should be copied to ``pymote_env/Lib/site-packages/`` directory::

    C:\Users\user\Desktop> xcopy /s matplotlib-1.2.0.win32-py2.7\PLATLIB\* %PYMOTE_ENV%\Lib\site-packages


Pyreadline
----------
For Pyreadline package use ``easy_install`` as ``pip`` currently installs version
1.7.1.dev-r0 which does not work well with IPython:

.. code-block:: bash

    (pymote_env)> easy_install pyreadline


PySide
------
For Pymote GUI part of the library PySide Qt bindings for Python should be installed. This is 
achieved `using this solution <http://stackoverflow.com/a/4673823/1247955>`__, that is, running 
following commands:

.. code-block:: bash

    (pymote_env)> easy_install PySide
    (pymote_env)> python pymote_env\Scripts\pyside_postinstall.py -install
    
Pymote
======
Finally, in order to download and install Pymote and all other required packages there are two
aviliable options, use one of them:

#. Development: to install latest development version of the Pymote use source from github repo::
    
    (pymote_env)> pip install -e git+https://github.com/darbula/pymote.git#egg=Pymote

#. Stable: for latest stable version use package from PyPI::
    
    (pymote_env)> pip install Pymote
    
.. _pymote-deps:

To list all packages installed in the environment run ``pip freeze``. The output should look 
something like this::

    (pymote_env)> pip freeze
    Pymote==0.1.1
    ipython==0.13.1
    matplotlib==1.2.0
    networkx==1.7
    numpy==1.6.2
    pypng==0.0.14
    pyreadline==1.7.1
    pyside==1.1.2
    scipy==0.11.0

For starting Pymote refer to :doc:`starting`.

.. 
    Ubuntu
    ******
    http://cysec.org/content/installing-matplotlib-and-numpy-virtualenv
    **TODO**.
    
    curl -O http://python-distribute.org/distribute_setup.py
    python distribute_setup.py
    easy_install pip

    Mac OSX
    *******

    **TODO** 

.. _virtualenv: http://www.virtualenv.org/