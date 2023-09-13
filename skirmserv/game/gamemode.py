"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skirmserv.game.game import Game
    from skirmserv.game.player import Player
    from skirmserv.game.team import Team


class Gamemode(object):
    def __init__(self, game: Game):
        self.game = game

        # Fields that have to be set by inheriting classes
        self.player_min = 0
        self.player_max = 255
        self.teams_managed = False

    # Events to override
    def player_joined(self, player: Player) -> None:
        """Override this method and handle what should happen when a player
        joined the game"""
        pass

    def player_leaving(self, player: Player) -> None:
        """Override this method and handle what should happen when a player
        will leave the game."""
        pass

    def player_game_start(self, player: Player) -> None:
        """Override this method. It will be called for every player in the
        game when the start gets scheduled."""
        pass

    def player_got_hit(self, player: Player, opponent: Player, sid: int) -> None:
        """Override this method and handle what should happen
        when a player (player) got hit by another player (opponent)."""
        pass

    def player_has_hit(self, player: Player, opponent: Player, sid: int) -> None:
        """Override this method and handle what should happen
        when a player (player) has hit someone else (opponent)."""
        pass

    def player_send_shot(self, player: Player, sid: int) -> None:
        """Override this method and handle what should happen when a player
        sends a shot."""
        pass

    def player_leaving_team(self, player: Player, team: Team):
        """Override this method and handle what should happen when a player
        leaves a team."""
        pass

    def player_joining_team(self, player: Player, team: Team):
        """Override this method and handle what should happen when a player
        joines a team."""
        pass

    def hitpoint_init(self, mode) -> tuple | None:
        """Override this method to init a hitpoint (will be called for mode 0 - 8).
        Return a color for the inited hitpoint or none if this mode is not
        required for the game"""
        pass

    def hitpoint_got_hit(self, mode: int, player: Player, sid: int) -> bool:
        """Override this method to handle what should happen when a player has
        hit a hitpoint. Return true if this hit was a valid hit."""
        return False

    def is_game_valid(self) -> bool:
        """Returns if the game assigned to this gamemode is valid
        and may be started."""

        # Check if there are enough but not too many players
        if self.game.get_player_count() < self.player_min:
            return False
        if self.game.get_player_count() > self.player_max:
            return False

        return True
