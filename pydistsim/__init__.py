from importlib import metadata

try:
    package_metadata = metadata.metadata("pydistsim")

    __author__ = package_metadata["author-email"]
    __version__ = package_metadata["version"]
except metadata.PackageNotFoundError:
    __author__ = __version__ = None

# For interactive sessions these import names with from pydistsim import *
import os

os.environ["QT_API"] = "pyside"
# Declare namespace package
from pkgutil import extend_path  # @Reimport

from pydistsim.conf import settings
from pydistsim.environment import Environment
from pydistsim.logger import set_log_level
from pydistsim.network import BidirectionalNetwork, Network
from pydistsim.networkgenerator import NetworkGenerator
from pydistsim.node import Node
from pydistsim.npickle import *
from pydistsim.sensor import CompositeSensor
from pydistsim.simulation import Simulation
from pydistsim.utils.localization import *

__path__ = extend_path(__path__, __name__)  # @ReservedAssignment
