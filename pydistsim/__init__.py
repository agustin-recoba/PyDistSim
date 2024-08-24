"""
Complete source for the pydistsim package.
"""

# flake8: noqa: F401

from importlib import metadata

try:
    package_metadata = metadata.metadata("pydistsim")

    __author__ = package_metadata["author-email"]
    __version__ = package_metadata["version"]
except metadata.PackageNotFoundError:
    __author__ = __version__ = None

# For interactive sessions these import names with from pydistsim import *
import os

try:
    from PySide6.QtCore import SIGNAL as __SIGNAL

    os.environ["QT_API"] = "pyside"
except ImportError:
    "No PySide6 found."
    ...

# Declare namespace package
from pkgutil import extend_path  # @Reimport

from pydistsim.algorithm import NodeAlgorithm, StatusValues
from pydistsim.benchmark import AlgorithmBenchmark
from pydistsim.logging import disable_logger, enable_logger, logger
from pydistsim.network import BidirectionalNetwork, Network, NetworkGenerator, Node
from pydistsim.simulation import Simulation

__path__ = extend_path(__path__, __name__)  # @ReservedAssignment
