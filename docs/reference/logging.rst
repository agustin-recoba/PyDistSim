.. _logging:
.. currentmodule:: pydistsim.logging

#########
Logging
#########

The logging module provides a flexible framework for emitting log messages from Python programs.
The log message is passed to the :attr:`logger` object, which handles the formatting and output of the message.
The logger is the entry point to the logging system.

By default, the logging module is disabled. To enable it, call the :func:`enable_logger` function.
This will enable the logger and set the log level to WARNING. To change the log level, call the
:func:`set_log_level` function.
