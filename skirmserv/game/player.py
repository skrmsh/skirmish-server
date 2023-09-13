"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skirmserv.game.game import Game
    from skirmserv.game.team import Team
    from skirmserv.communication.client import SocketClient

from logging import getLogger


class Player(object):
    def __init__(self, game: Game, client: SocketClient):
        # Reference to game and team
        self.game = game
        self.team = None

        self.client = client

        # Fields required by the skirmish protocol
        self.pid = self.game.get_next_pid()
        self.name = self.client.user.name
        self.health = 0
        self.points = 0
        self.color = [0, 0, 0]  # color_r, color_g, color_b
        self.color_before_game = False
        self.ammo_limit = False
        self.ammo = 0
        self.phaser_enable = False
        self.phaser_disable_until = 0
        self.max_shot_interval = 1000
        self.inviolable = False
        self.inviolable_until = 0
        self.inviolable_lights_off = True

    def get_pgt_data(self) -> dict:
        """Generates a dict containing all fields in pgt format"""
        return {
            "p_id": self.pid,
            "p_n": self.name,
            "p_h": self.health,
            "p_p": self.points,
            "p_cr": self.color[0],
            "p_cg": self.color[1],
            "p_cb": self.color[2],
            "p_cbg": self.color_before_game,
            "p_al": self.ammo_limit,
            "p_a": self.ammo,  # todo: set only diff for ammo or
            # some other solution?
            "p_pe": self.phaser_enable,
            "p_pdu": int(self.phaser_disable_until),
            "p_msi": self.max_shot_interval,
            "p_r": self.get_rank(),
            "p_i": self.inviolable,
            "p_iu": int(self.inviolable_until),
            "p_ilo": self.inviolable_lights_off,
        }

    def add_ammo(self, amount: int) -> None:
        """Triggers the add ammo action on the phaser with the given amount"""
        self.client.trigger_action(self.client.ACTION_ADD_AMMO, amount=amount)

    def get_rank(self) -> int:
        """Returns the rank of this player"""
        return self.game.get_player_rank(self)

    def change_team(self, team: Team) -> None:
        """Changes Team if the player is currently part of a team
        or joins a team when the player is not part of a team"""
        if self.team is None:
            team.join(self)
            self.team = team
        else:
            self.team.leave(self)
            team.join(self)
            self.team = team

    def send_shot(self, sid: int) -> None:
        """This function is called when the phaser calls the
        Send Shot action with sid parameter."""
        self.game.gamemode.player_send_shot(self, sid)

        getLogger(__name__).debug(
            "Player %s send shot %d in game %s", str(self), sid, str(self.game)
        )

        for spectator in self.game.spectators:
            spectator.player_fired_shot(self, sid)

    def got_hit(self, pid: int, sid: int) -> None:
        """This function is called when the phaser/breast calls the
        Got Hit action with sid/pid parameter."""

        # Get the opponent by player id
        opponent = self.game.get_player_by_pid(pid)

        # do not act if the opponent doesn't exist
        if opponent is None:
            return

        # Let the gamemode handle this event
        # but first check if this shot has never hit before
        if not self.game.is_first_hit(self, sid):
            self.game.gamemode.player_got_hit(self, opponent, sid)

            # Also let the gamemode handle the event that the
            # other player has hit
            self.game.gamemode.player_has_hit(opponent, self, sid)

        # inform both clients about updates
        self.client.update()
        opponent.client.update()

        getLogger(__name__).debug(
            "Player %s got hit by %s in game %s",
            str(self),
            str(opponent),
            str(self.game),
        )

        self.game.update_spectators()
        for spectator in self.game.spectators:
            spectator.player_got_hit(self, opponent, sid)

    def __str__(self):
        return "{0} ({1})".format(self.name, self.pid)
