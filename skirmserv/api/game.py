"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skirmserv.models.user import UserModel
    from skirmserv.game.game import Game

from flask_restful import Resource
from flask_restful import reqparse
from flask import request
from flask_restful import abort

from skirmserv.game.game_manager import GameManager
from skirmserv.api import requires_auth

from flasgger import swag_from

game_create_reqparse = reqparse.RequestParser()
game_create_reqparse.add_argument(
    "gamemode", type=str, help="Gamemode field is required!", required=True
)

game_start_reqparser = reqparse.RequestParser()
game_start_reqparser.add_argument(
    "delay", type=int, help="Delay field is required!", required=True
)


def abort_if_game_is_not_owned(user: UserModel, game: Game):
    """Aborts if the game was not created by the given user"""
    if game.created_by.id != user.id:
        abort(403, message="This game was not created by you!")


def get_game_or_abort(gid: str) -> Game | None:
    game = GameManager.get_game(gid)
    if game is None:
        abort(404, message="Game not found!")

    return game


class GameAPI(Resource):
    @requires_auth
    @swag_from("openapi/game/get.yml")
    def get(self, user: UserModel, gid: str):
        """
        Returns information about the requested game
        """

        # Get game by gid
        game = get_game_or_abort(gid)

        abort_if_game_is_not_owned(user, game)

        teams = []
        for team in game.teams.values():
            teams.append(
                {
                    "tid": team.tid,
                    "player_count": team.get_player_count(),
                    "points": team.get_points(),
                    "rank": team.get_rank(),
                    "name": team.name,
                }
            )

        players = []
        for player in game.players.values():
            players.append(
                {
                    "pid": player.pid,
                    "name": player.name,
                    "points": player.points,
                    "health": player.health,
                    "rank": player.get_rank(),
                }
            )

        return {
            "gid": game.gid,
            "start_time": game.start_time,
            "player_count": game.get_player_count(),
            "team_count": game.get_team_count(),
            "valid": game.gamemode.is_game_valid(),
            "created_at": game.created_at,
            "created_by": game.created_by.name,
            "teams": teams,
            "players": players,
        }, 200

    @requires_auth
    @swag_from("openapi/game/post.yml")
    def post(self, gid: str, user: UserModel):
        """Creates a new game, ignores the gid parameter"""
        args = game_create_reqparse.parse_args()

        gid = GameManager.create_game(args.get("gamemode"), user)

        return {"gid": gid}, 201

    @requires_auth
    @swag_from("openapi/game/put.yml")
    def put(self, gid: str, user: UserModel):
        """Starts the game in "delay" seconds"""
        args = game_start_reqparser.parse_args()

        game = get_game_or_abort(gid)

        is_scheduled = game.schedule_start(args.get("delay"))

        if is_scheduled:
            return {}, 204
        else:
            abort(409, message="The game is currently not valid to start")

    @requires_auth
    @swag_from("openapi/game/delete.yml")
    def delete(self, gid: str, user: UserModel):
        """Deletes the game"""

        game = get_game_or_abort(gid)
        abort_if_game_is_not_owned(user, game)

        game.close()

        return {}, 204


class GamesAPI(Resource):
    def get(self):
        """Get all currently running games"""

        result = {"games": []}
        for gid in GameManager.get_instance().games:
            game = GameManager.get_game(gid)
            result["games"].append(
                {
                    "gid": game.gid,
                    "start_time": game.start_time,
                    "player_count": game.get_player_count(),
                    "team_count": game.get_team_count(),
                    "valid": game.gamemode.is_game_valid(),
                    "created_at": game.created_at,
                    "created_by": game.created_by.name,
                }
            )

        return result, 200
