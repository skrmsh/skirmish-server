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

        # Set for already hit shots
        self._already_hit = set()

        # Fields that have to be set by inheriting classes
        self.player_min = 0
        self.player_max = 255
        self.teams_managed = False

    # Helper methods
    def mark_shot_hit(self, player: Player, sid: int) -> None:
        """Marks that the given shot has hit someone"""
        psid = sid << 8 | player.pid  # Combined player / shot id
        self._already_hit.add(psid)

    def has_shot_hit(self, player: Player, sid: int) -> bool:
        """Returns if the given shot has already hit someone"""
        psid = sid << 8 | player.pid  # Combined player / shot id
        return psid in self._already_hit

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

    def is_game_valid(self) -> bool:
        """Returns if the game assigned to this gamemode is valid
        and may be started."""

        # Check if there are enough but not too many players
        if self.game.get_player_count() < self.player_min:
            return False
        if self.game.get_player_count() > self.player_max:
            return False

        return True
