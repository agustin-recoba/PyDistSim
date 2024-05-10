from enum import StrEnum

import loguru

logger = loguru.logger


class LogLevels(StrEnum):
    """
    Enum class representing different log levels.
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
