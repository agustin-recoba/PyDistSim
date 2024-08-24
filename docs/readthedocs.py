# Readthedocs default blue theme
html_style = None

# Mock modules that are not present on readthedocs
# http://read-the-docs.readthedocs.org/en/latest/faq.html#i-get-import-errors-on-libraries-that-depend-on-c-modules
import sys


def get_mock(mod_name):

    class Mock:
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            return Mock()

        @classmethod
        def __getattr__(cls, name: str):
            mock_type_name = name[0].upper() + name[1:]
            mockType = type(mock_type_name, (Mock,), {})
            mockType.__module__ = cls.__module__

            if name in ("__file__", "__path__"):
                return "/dev/null"
            elif name[0] == name[0].upper():
                return mockType
            else:
                return mockType()

        def __or__(self, other):
            return self.__class__()

    Mock.__name__ = mod_name
    Mock.__module__ = mod_name

    return Mock()


MOCK_MODULES = [
    "png",
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "scipy",
    "scipy.stats",
    "scipy.constants",
    "loguru",
    "pandas",
    "seaborn",
    "pytest",
]
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = get_mock(mod_name)
