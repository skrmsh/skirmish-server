"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skirmserv.game.game import Game
    from skirmserv.game.player import Player

from logging import getLogger


class Team(object):
    def __init__(self, game: Game, tid: int, name: str):
        self.game = game
        self.players = set()

        self.tid = tid
        self.name = name

    def get_pgt_data(self) -> dict:
        """Generates a dict containing all fields in pgt format"""
        return {
            "t_id": self.tid,
            "t_pc": self.get_player_count(),
            "t_p": self.get_points(),
            "t_r": self.get_rank(),
            "t_n": self.name,
        }

    def get_points(self) -> int:
        """Returns the sum of points from every player"""
        result = 0
        for player in self.players:
            result += player.points
        return result

    def get_rank(self) -> int:
        """Returns the rank of this team"""
        return self.game.get_team_rank(self)

    def get_player_count(self) -> int:
        """Returns the amount of players in this team"""
        return len(self.players)

    def join(self, player: Player):
        """Adds a new player to this team"""
        self.players.add(player)
        player.team = self

        getLogger(__name__).debug("Joined player %s to team %s", str(player), str(self))

    def leave(self, player: Player):
        """Removes a player from this team"""
        if player in self.players:
            self.players.remove(player)
            player.team = None

            getLogger(__name__).debug(
                "Removed player %s from team %s", str(player), str(self)
            )

    def __str__(self):
        return "{0} ({1})".format(self.name, self.tid)
