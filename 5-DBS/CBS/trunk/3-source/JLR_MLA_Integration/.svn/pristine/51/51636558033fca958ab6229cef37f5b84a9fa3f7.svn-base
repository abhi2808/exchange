"""
:: NAME:           dbs.py
:: FUNCTION:       To generate dbs jenkins configuration
:: PROJECT:        Daily Build System
:: DEVELOPED BY :  Abhishek Srivastava
::
"""

import os
import sys
import time
import subprocess


sys.path.append(os.path.join(os.path.split(sys.argv[0])[0], '..', 'DailyBuildSystem'))
try:
    from dbs import DBs
except:
    from DailyBuildSystem.dbs import DBS


class ReleaseException:
    pass


class Release:
    SVN_MAX_DEPTH = 4

    def __init__(self, binary_path: str, app_path: str, app_file: str, dbs_conf: str = None):
        self._binary = binary_path

