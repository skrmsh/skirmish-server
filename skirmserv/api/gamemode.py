"""
Skirmish Server

Copyright (C) 2022-2023 Ole Lange
"""

from flask_restful import Resource
from flask_restful import reqparse
from flask import request
from flask_restful import abort

from flasgger import swag_from

from skirmserv.gamemodes import available_gamemodes


class GamemodeAPI(Resource):
    @swag_from("openapi/game/gamemodes_get.yml")
    def get(self):
        """Returns all available gamemodes"""

        gm_strings = list(available_gamemodes.keys())

        return {"gamemodes": gm_strings}, 200
