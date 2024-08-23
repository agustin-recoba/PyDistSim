import unittest

from pydistsim.logging import LogLevels, disable_logger, enable_logger, set_log_level


class PyDistSimTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_log_level(LogLevels.DEBUG)
        enable_logger()

    @classmethod
    def tearDownClass(cls):
        set_log_level(LogLevels.INFO)
        disable_logger()
