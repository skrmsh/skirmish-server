"""
Skirmish Server

Team API Endpoint

Copyright (C) 2023 Ole Lange
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skirmserv.models.user import UserModel
    from skirmserv.game.game import Game
    from skirmserv.game.player import Player

from skirmserv.game.team import Team
from skirmserv.game.game_manager import GameManager

from skirmserv.api import requires_auth

from flask_restful import Resource
from flask_restful import abort
from flask_restful import reqparse

team_create_reqparse = reqparse.RequestParser()
team_create_reqparse.add_argument(
    "name", type=str, help="Team name field is required!", required=True
)

team_move_reqparse = reqparse.RequestParser()
team_move_reqparse.add_argument(
    "pid", type=int, help="Player id field is required!", required=True
)


def abort_if_game_is_not_owned(user: UserModel, game: Game):
    """Aborts if the game was not created by the specified user"""
    if game.created_by.id != user.id:
        abort(403, message="You don't own this game!")


def abort_if_gamemode_manages_teams(game: Game):
    """Aborts if the gamemode of the game manages the teams"""
    if game.gamemode.teams_managed:
        abort(403, message="Teams in this game are managed by the gamemode")


def get_game_or_abort(gid: str) -> Game | None:
    """Get the specified game by gid or abort the request with 404"""
    game = GameManager.get_game(gid)
    if game is None:
        abort(404, message="Game not found!")

    return game


def get_team_or_abort(game: Game, tid: int) -> Team | None:
    """Get the specified team or abort the request with 404"""
    team = game.teams.get(tid, None)
    if team is None:
        abort(404, message="Team not found!")

    return team


def get_player_or_abort(game: Game, pid: int) -> Player | None:
    """Get the specified player or abort the request with 404"""
    player = game.players.get(pid, None)
    if player is None:
        abort(404, message="Player not found!")

    return player


class TeamAPI(Resource):
    @requires_auth
    def get(self, user: UserModel, gid: str, tid: int):
        """Returns information about the requested team"""

        # Get game by gid and team by tid
        game = get_game_or_abort(gid)
        abort_if_game_is_not_owned(user, game)

        team = get_team_or_abort(game, tid)

        return {
            "tid": team.tid,
            "game": game.gid,
            "player_count": team.get_player_count(),
            "points": team.get_points(),
            "rank": team.get_rank(),
            "name": team.name,
        }, 200

    @requires_auth
    def post(self, user: UserModel, gid: str, tid: int):
        """Creates a new team"""

        # Get game
        game = get_game_or_abort(gid)
        abort_if_game_is_not_owned(user, game)
        abort_if_gamemode_manages_teams(game)

        args = team_create_reqparse.parse_args()
        name = args.get("name")

        for team in game.teams.values():
            if team.name == name:
                return {"message": "There is already a team with this name!"}, 409

        team = Team(game, game.get_next_tid(), name)
        game.add_team(team)

        return {
            "tid": team.tid,
            "game": game.gid,
            "player_count": team.get_player_count(),
            "points": team.get_points(),
            "rank": team.get_rank(),
            "name": team.name,
        }, 200

    @requires_auth
    def put(self, user: UserModel, gid: str, tid: int):
        """Moves a player to the specified team |
        Removes a player from all teams if the tid is 0"""

        # Get game
        game = get_game_or_abort(gid)
        abort_if_game_is_not_owned(user, game)
        abort_if_gamemode_manages_teams(game)

        # Get player
        args = team_move_reqparse.parse_args()
        player = get_player_or_abort(game, args.pid)

        # Move player if tid is not zero
        if tid != 0:
            team = get_team_or_abort(game, tid)
            game.move_player_to_team(player, team)

            return {"message": "Moved player to team"}, 200

        # Remove player from current team if tid is zero
        else:
            if player.team is not None:
                player.team.leave(player)

            return {"message": "Removed player from team"}, 200

    @requires_auth
    def delete(self, user: UserModel, gid: str, tid: int):
        """Removes all players from the team and deletes the team"""

        # Get Game
        game = get_game_or_abort(gid)
        abort_if_game_is_not_owned(user, game)
        abort_if_gamemode_manages_teams(game)

        team = get_team_or_abort(game, tid)
        game.remove_team(team)

        return {}, 204
