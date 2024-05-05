from importlib import metadata

try:
    package_metadata = metadata.metadata("pymote")

    __author__ = package_metadata["author-email"]
    __version__ = package_metadata["version"]
except metadata.PackageNotFoundError:
    __author__ = __version__ = None

# For interactive sessions these import names with from pymote import *
import os

os.environ["QT_API"] = "pyside"
# Declare namespace package
from pkgutil import extend_path  # @Reimport

from pymote.conf import settings
from pymote.environment import Environment
from pymote.network import Network
from pymote.networkgenerator import NetworkGenerator
from pymote.node import Node
from pymote.npickle import *
from pymote.sensor import CompositeSensor
from pymote.simulation import Simulation
from pymote.utils.localization import *

__path__ = extend_path(__path__, __name__)  # @ReservedAssignment
