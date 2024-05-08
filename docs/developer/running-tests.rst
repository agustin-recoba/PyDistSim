Running tests
=============

All python packages mencioned in this tutorial should already be installed in your environment if
you followed the guide at ":ref:`installation`".

To execute tests, pytest must be installed.
All tests should be automatically found by recursively scanning directories.

To run all tests run this from root pydistsim directory::

    pytest

To run selected test module::

    pytest pydistsim/tests/test_algorithm.py

or selected test case::

    pytest pydistsim/tests/test_algorithm.py::TestAlgorithmsSetter

Tests coverage
--------------
For tests coverage, ``pytest-cov`` and ``coverage`` are needed.
By default, coverage is collected in all test runs. To get coverage report, run::

    coverage report --show-missing

Make report in console or html::

    coverage report -m
    coverage html

For integration with `coveralls <https://coveralls.io>`_ we use the `Universal Coverage Reporter <https://github.com/coverallsapp/coverage-reporter>`_. This is configured in file ``.travis.yml``.

To change the described ``pytest`` behabiour, see section ``[tool.pytest.ini_options]`` at ``pyproject.toml``.
