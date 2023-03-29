"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skirmserv.game.player import Player
    from skirmserv.game.game import Game

from skirmserv.game.gamemode import Gamemode

import time
import colorsys


class GMDebug(Gamemode):
    """
    Debug gamemode
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.player_min = 1

        self._already_hit = set()

        self._inviolable_time = 2  # How many seconds inviolable after got hit

    def player_joined(self, player: Player) -> None:
        player.health = 100
        player.points = 0
        player.color_before_game = True

    def player_game_start(self, player: Player) -> None:
        # set player color
        # +1 to prevent that the first and last player have the same color
        hue = self.game.get_player_index(player) / (self.game.get_player_count() + 1)
        norm_rgb = colorsys.hsv_to_rgb(hue, 1, 1)
        rgb = list(map(lambda x: int(x * 255), norm_rgb))
        player.color = rgb

        player.max_shot_interval = 300

        # Player is inviolable until the game starts
        player.inviolable = False
        player.inviolable_until = self.game.start_time

        # Phaser is disabled until start time
        player.phaser_enable = True
        player.phaser_disable_until = self.game.start_time

    def player_got_hit(self, player: Player, opponent: Player, sid: int) -> None:
        # Check if this sid has already hit another player
        if self.has_shot_hit(player, sid):
            return

        self.mark_shot_hit(player, sid)

        player.phaser_disable_until = time.time() + self._inviolable_time
        player.inviolable_until = player.phaser_disable_until

        player.client.current_actions.add(player.client.ACTION_HIT_VALID)

    def player_has_hit(self, player: Player, opponent: Player, sid: int) -> None:
        player.points += 500
        player.client.current_actions.add(player.client.ACTION_SHOT_HIT)
