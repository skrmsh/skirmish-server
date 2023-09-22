"""
Skirmish Server

This file is imported by flask to load the configuration. This file loads
from the config_keys list the according environment variables and stores
them in same called variables
"""

import os

default_config = {
    # Misc
    "SECRET_KEY": "",  # Flask Secret Key
    "LOGGING_LEVEL": "INFO",
    ## Database
    "DB_TYPE": "sqlite",  # Database type (one of sqlite, mysql, postgresql)
    # Keys for DB_TYPE mysql
    "DB_LOCATION": "db_dev.sqlite3",  # Database path
    # Keys for DB_TYPE mysql or postgresql
    "DB_HOST": None,
    "DB_PORT": None,
    "DB_DATABASE": None,
    "DB_USER": None,
    "DB_PASS": None,
}

_g = globals()
for key in default_config:
    _g[key] = os.environ.get(key, default_config[key])
