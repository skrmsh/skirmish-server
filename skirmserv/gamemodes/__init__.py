"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from skirmserv.gamemodes.deathmatch import Deathmatch
from skirmserv.gamemodes.gmdebug import GMDebug

# Dict containing all available Gamemodes with their names as key
available_gamemodes = {
    "deathmatch": Deathmatch,
    "debug": GMDebug
}