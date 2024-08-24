Writing documentation
*********************
This section describes certain not obvious details in writing documentation for PyDistSim in sphinx.

Build locally
=============

To build the documentation locally, create a new virtual environment and install the requirements from ``docs/requirements.txt``.
Then run ``make html`` in the ``docs`` directory.

The documentation will be built in ``docs/_build/html``.


Intersphinx
===========

To auto-reference external document in with intersphinx in docs, use ```:py:<type>:`<ref>``` i.e. ``:py:class:`numpy.poly1d```.

The intersphinx mapping is defined in ``source/conf.py``. The mapping is defined as a dictionary with the key being the name of the
mapping and the value being the URL of the mapping. Automatic population of the mapping is done with the extension ``seed_intersphinx_mapping``.


readthedocs.org
==============

To add the documentation to readthedocs.org, create an account and add the repository. The documentation will be built automatically
since the configuration file ``.readthedocs.yml`` is present in the repository.
