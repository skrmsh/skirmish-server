from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skirmserv.game.player import Player

from flask_socketio import SocketIO  # Just for typing
from skirmserv.game.game import Game

import json
from logging import getLogger


class Spectator(object):
    def __init__(self, socket_id: str, game: Game, socketio: SocketIO):
        self.socket_id = socket_id
        self.game = game

        self.socketio = socketio

        self.game.spectators.add(self)

        self.update()

    def close(self):
        """
        Removes the instance from the games list of spectators
        """
        self.game.spectators.remove(self)
        getLogger(__name__).debug("Closed spectator %s", str(self))

    def update(self):
        """
        Updates all data for the spectator
        """
        players = [self.game.players[p].get_pgt_data() for p in self.game.players]
        teams = [self.game.teams[t].get_pgt_data() for t in self.game.teams]
        self.socketio.emit(
            "spectate",
            json.dumps(
                {
                    "pgt": {
                        "game": self.game.get_pgt_data(),
                        "players": players,
                        "teams": teams,
                    }
                }
            ),
            to=self.socket_id,
        )
        getLogger(__name__).debug("Updated spectator %s", str(self))

    def player_got_hit(self, player: Player, opponent: Player, sid: int, hp: int = 7):
        self.socketio.emit(
            "spectate",
            json.dumps(
                {
                    "hit": {
                        "player": player.get_pgt_data(),
                        "by": opponent.get_pgt_data(),
                        "sid": sid,
                        "hp": hp,
                    }
                }
            ),
            to=self.socket_id,
        )
        getLogger(__name__).debug(
            "Informed spectator %s that player %s got hit", str(self), str(player)
        )

    def player_fired_shot(self, player: Player, sid: int) -> None:
        self.socketio.emit(
            "spectate",
            json.dumps({"shot": {"player": player.get_pgt_data(), "sid": sid}}),
            to=self.socket_id,
        )
        getLogger(__name__).debug(
            "Informed spectator %s that player %s fired a shot", str(self), str(player)
        )

    def __str__(self):
        return "{0} ({1})".format(self.game, self.socket_id)
