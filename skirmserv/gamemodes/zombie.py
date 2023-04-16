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
from skirmserv.game.team import Team

import time
import random


class Zombie(Gamemode):
    """ """

    def __init__(self, game: Game):
        super().__init__(game)

        self.player_min = 2
        self.teams_managed = True

        self.team_zombie = Team(self.game, self.game.get_next_tid(), "Zombie")
        self.game.add_team(self.team_zombie)

        self.team_alive = Team(self.game, self.game.get_next_tid(), "Alive")
        self.game.add_team(self.team_alive)

        self.initial_zombie = None
        self.new_game_delay = 0

    def player_joined(self, player: Player) -> None:
        player.health = 100
        player.points = 0
        player.color_before_game = True
        player.inviolable_lights_off = False

    def player_game_start(self, player: Player) -> None:
        if self.initial_zombie is None:
            player_list = list(self.game.players.keys())
            self.initial_zombie = random.choice(player_list)

        if player.pid == self.initial_zombie:
            player.color = [0, 255, 0]
            player.health = 0
            player.inviolable = True
            player.inviolable_until = 0
            player.phaser_enable = True
            player.phaser_disable_until = self.game.start_time + self.new_game_delay
            self.game.move_player_to_team(player, self.team_zombie)
        else:
            player.color = [0, 0, 0]
            player.health = 100
            player.inviolable = False
            player.inviolable_until = self.game.start_time + self.new_game_delay
            player.phaser_enable = False
            player.phaser_disable_until = 0
            self.game.move_player_to_team(player, self.team_alive)

        player.max_shot_interval = 300
        print(player.color)

    def player_got_hit(self, player: Player, opponent: Player, sid: int) -> None:
        # Check if this sid has already hit another player
        if self.has_shot_hit(player, sid):
            return

        self.mark_shot_hit(player, sid)

        if player.team == self.team_alive and opponent.team == self.team_zombie:
            player.color = [0, 255, 0]
            player.health = 0
            player.inviolable = True
            player.inviolable_until = 0
            player.phaser_enable = True
            player.phaser_disable_until = 0
            self.game.move_player_to_team(player, self.team_zombie)

            """
            if self.team_alive.get_player_count() == 0:
                self.initial_zombie = None
                self.new_game_delay = 30
                self.game.start_time = time.time()
                for player in self.game.players.values():
                    self.player_game_start(player)
                    player.client.update()
            """

        player.client.current_actions.add(player.client.ACTION_HIT_VALID)

    def player_has_hit(self, player: Player, opponent: Player, sid: int) -> None:
        if player.team == self.team_zombie:
            player.points += 100

        player.client.current_actions.add(player.client.ACTION_SHOT_HIT)
        player.client.current_data.update({"name": opponent.name})
