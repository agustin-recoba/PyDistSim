"""
Logger configuration for the package.
"""

import sys
from enum import StrEnum

import loguru

logger = loguru.logger
"Loguru logger instance for the package."


class LogLevels(StrEnum):
    """
    Enum class representing different log levels.
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LevelFilter:
    def __init__(self, level: LogLevels):
        self.level = level

    def __call__(self, record):
        level_no = logger.level(self.level).no
        return record["level"].no >= level_no


main_filter = LevelFilter(LogLevels.WARNING)

logger.remove()

stdout_handler = logger.add(sys.stdout, filter=main_filter, level=0)

logger.disable("pydistsim")


def set_log_level(level: LogLevels):
    main_filter.level = level


def enable_logger():
    logger.enable("pydistsim")


def disable_logger():
    logger.disable("pydistsim")
