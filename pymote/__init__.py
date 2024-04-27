from pymote import release

__author__ = "%s <%s>" % release.authors["Arbula"]
__license__ = release.license
__version__ = release.version

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
