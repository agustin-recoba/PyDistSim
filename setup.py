import os
import sys

from setuptools import setup

# transfer profile_pydistsim for ipython into IPYTHONDIR
if "install" in sys.argv or "develop" in sys.argv:
    import shutil

    try:
        from IPython.paths import get_ipython_dir

        ipythondir = get_ipython_dir()
    except ImportError:  # @ReservedAssignment
        print(
            "PyDistSim IPython configuration not installed. Install latest "
            "IPython and then copy the conf/ipython/profile_pydistsim/"
            "ipython_config.py manually to IPython config dir."
        )
    else:
        profiledir = os.path.join(ipythondir, "profile_pydistsim")
        if not os.path.exists(ipythondir):
            os.makedirs(ipythondir)
        if not os.path.exists(profiledir):
            os.makedirs(profiledir)
        print("copying ipython_config.py and ipython_notebook_config.py to " + profiledir)
        shutil.copy(
            os.path.join("pydistsim", "conf", "ipython", "ipython_config.py"),
            profiledir,
        )
        shutil.copy(
            os.path.join("pydistsim", "conf", "ipython", "ipython_notebook_config.py"),
            profiledir,
        )

setup()
