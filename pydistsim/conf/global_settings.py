"""Default PyDistSim settings.

Override these with settings in the module pointed-to by the
``PYDISTSIM_SETTINGS_MODULE`` environment variable or by using
``settings.configure(**settings)`` or ``settings.load('path.to.settings')``

"""

import scipy.stats
from numpy import pi

# **NETWORK*

#: 2-dimensional environment is currently only supported environment.
ENVIRONMENT = "Environment2D"

#: default environment dimensions
ENVIRONMENT2D_SHAPE = (600, 600)

#: default number of nodes, used in
#: :class:`pydistsim.network.generator.NetworkGenerator`.
N_COUNT = 100

#: No algorithms defined by default.
ALGORITHMS = ()

#: Default edge type
DIRECTED = False

#: Unit disc graph is the default channel type.
CHANNEL_TYPE = "UdgRangeType"

#: Absolute tolerance of network degree
DEG_ATOL = 1

# Node

#: Default communication range of nodes.
COMM_RANGE = 100

#: By default nodes have no sensors.
SENSORS = ()

#: Not implemented yet
ACTUATORS = ()

#: Probability function (by default :py:data:`scipy.stats.norm`) and its
#: parameters for :class:`pydistsim.network.sensor.AoASensor`
AOA_PF_PARAMS = {"pf": scipy.stats.norm, "scale": 10 * pi / 180}  # in radians

#: Probability function (by default :py:data:`scipy.stats.norm`) and its
#: :class:`pydistsim.network.sensor.DistSensor`
DIST_PF_PARAMS = {"pf": scipy.stats.norm, "scale": 10}
