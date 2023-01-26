"""
Skirmish Server

Copyright (C) 2022-2023 Ole Lange
"""

from flask_restful import Resource
from flask_restful import reqparse
from flask import request
from flask_restful import abort

from skirmserv.gamemodes import available_gamemodes

class GamemodeAPI(Resource):

    def get(self):
        """Returns all available gamemodes"""
        
        gm_strings = list(available_gamemodes.keys())

        return {
            "gamemodes": gm_strings
        }, 200