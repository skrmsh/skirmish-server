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
import random

class Deathmatch(Gamemode):
    """
    Deathmatch Gamemode:
    All players against each other. Each player has it's own color.
    Everybody starts with full health and loses 10 health per hit. After
    a player was hit the player is 5 seconds inviolable and the player
    cannot fire shots for 5 seconds.

    If the player has no health left the phaser turns off and the player
    is removed from the game. The game is finished if only one player survived
    """
    
    def __init__(self, game: Game):
        super().__init__(game)

        self.player_min = 2

        # Variable to offset every players hue value
        self.color_offset = random.randint(0, 100) / 100.0

        self._already_hit = set()

        self._inviolable_time = 6 # How many seconds inviolable after got hit
    
    def player_joined(self, player: Player) -> None:
        player.health = 100
        player.points = 0
        player.color_before_game = True

    def player_game_start(self, player: Player) -> None:
        # set player color
        # +1 to prevent that the first and last player have the same color
        hue = self.game.get_player_index(player) / (self.game.get_player_count() + 1)
        hue = (hue + self.color_offset) % 1
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
        if self.has_shot_hit(player, sid): return

        self.mark_shot_hit(player, sid)

        # If the player will survive this shot
        if player.health > 10:
            player.health -= 10
            player.inviolable_until = time.time() + self._inviolable_time
            player.phaser_disable_until = player.inviolable_until

        # If the player is dead after this shot
        else:
            player.health = 0
            player.inviolable = True
            player.phaser_enable = False
            player.color = [0, 0, 0]

        player.client.current_actions.add(player.client.ACTION_HIT_VALID)
    
    def player_has_hit(self, player: Player, opponent: Player, sid: int) -> None:

        # Normal Hit
        if opponent.health > 0:
            player.points += 100

        # Killing Shot
        elif opponent.health == 0:
            player.points += 500

        player.client.current_actions.add(player.client.ACTION_SHOT_HIT)
        player.client.current_data.update({"name": opponent.name})