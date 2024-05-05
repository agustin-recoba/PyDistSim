import logging
import logging.config
from enum import IntEnum


class LogLevels(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


LOG_CONFIG = {
    "version": 1,
    "loggers": {
        "pymote": {
            "level": LogLevels.WARNING,
            "handlers": ["fileHandler", "consoleHandler"],
        },
        "pymote.simulation": {
            "level": LogLevels.DEBUG,
            "handlers": ["simFileHandler"],
            "propagate": 1,
        },
    },
    "handlers": {
        "fileHandler": {
            "class": "logging.FileHandler",
            "level": LogLevels.DEBUG,
            "formatter": "fileFormatter",
            "filename": "pymote.log",
        },
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "formatter": "consoleFormatter",
            "stream": "ext://sys.stdout",
        },
        "simFileHandler": {
            "class": "logging.FileHandler",
            "level": LogLevels.DEBUG,
            "formatter": "fileFormatter",
            "filename": "simulation.log",
        },
    },
    "formatters": {
        "fileFormatter": {
            "format": ("%(asctime)s - %(levelname)s:" "[%(filename)s] %(message)s"),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "consoleFormatter": {
            "format": ("%(levelname)-8s" "[%(filename)s]: %(message)s"),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}

logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger("pymote")
