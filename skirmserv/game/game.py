"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from skirmserv.game.player import Player
    from skirmserv.game.team import Team
    from skirmserv.game.gamemode import Gamemode
    from skirmserv.models.user import UserModel

import time


class Game(object):
    def __init__(self, gamemode: Type[Gamemode], gid: str, created_by: UserModel):
        self.gid = gid

        self.created_by = created_by
        self.created_at = time.time()

        # Timestamp for the scheduled start
        # 0 -> no start scheduled
        self.start_time = 0

        # Sets of players and teams which are part of this game
        self.players = {}
        self.teams = {}

        # Spectators spectating this game
        self.spectators = set()

        self.gamemode = gamemode(self)  # Creates a new instance of the gamemode

    def update_spectators(self) -> None:
        """Updates all spectators for this game"""
        for spectator in self.spectators:
            spectator.update()

    def get_pgt_data(self) -> dict:
        """Generates a dict containing all fields in pgt format"""
        return {
            "g_gid": self.gid,
            "g_player_count": self.get_player_count(),
            "g_team_count": self.get_team_count(),
            "g_start_time": int(self.start_time),
            "g_created_at": int(self.created_at),
            "g_created_by": self.created_by.name,
        }

    def get_next_pid(self) -> int:
        """Returns the next available player id"""

        # If its the first player return 1
        if len(self.players) == 0:
            return 1
        # Its generated by getting the highest player id ever added and adding 1
        return max(self.players.keys()) + 1

    def get_next_tid(self) -> int:
        """Returns the next available team id"""

        print("Noch alle latten am zaun?")
        print(dir(self))

        # If its the first team return 1
        if len(self.teams) == 0:
            return 1

        # Else return the max team id + 1 (same way as pid)
        return max(self.teams.keys()) + 1

    def get_player_by_pid(self, pid: int) -> Player:
        """Returns the player with the given pid from this game"""
        return self.players.get(pid, None)

    def add_player(self, player: Player) -> None:
        """Adds the given player to this game"""
        self.players.update({player.pid: player})
        self.gamemode.player_joined(player)
        self.update_spectators()

    def remove_player(self, player: Player) -> None:
        """Removes the given player from this game"""
        self.players.pop(player.pid)
        self.gamemode.player_leaving(player)
        self.update_spectators()

    def add_team(self, team: Team) -> None:
        self.teams.update({team.tid: team})
        self.update_spectators()

    def move_player_to_team(self, player: Player, team: Team) -> None:
        # Remove player from current team
        if player.team is not None:
            player.team.leave(player)
        # Add it to the new team
        team.join(player)

    def schedule_start(self, delay: int) -> bool:
        """Schedules the game start in delay seconds"""
        if not self.gamemode.is_game_valid():
            return False

        self.start_time = time.time() + delay

        for player in self.players.values():
            # Let the gamemode handle things that happen on game start
            self.gamemode.player_game_start(player)

            # Inform the player about updates
            player.client.update()

        self.update_spectators()

        return True

    def close(self) -> None:
        """Close this game"""
        for player in self.players:
            self.gamemode.player_leaving(player)
            player.client.update()

        del self.players
        del self.teams
        self.players = {}
        self.teams = {}
        print("DEL??")

        for spectator in self.spectators:
            spectator.update()
            spectator.close()

    def get_team_rank(self, team: Team) -> int:
        """Returns the rank of the given team. Returns -1 if the
        Team is not part of this game"""

        # Return -1 if the team is not part of this game
        if not team in self.teams.values():
            return -1

        # Creating a list of teams (to be able to order them)
        # then sort it by points and then reversing the order so
        # that the first item is the first rank and so on
        team_list = list(self.teams.values())
        team_list.sort(key=lambda x: x.get_points())
        team_list = team_list[::-1]

        # Rank is the index of the team_list. + 1 is added that the
        # first place is not 0 but 1
        rank = team_list.index(team) + 1

        return rank

    def get_player_rank(self, player: Player) -> int:
        """Returns the rank of the given player. Returns -1 if the
        player is not part of this game"""

        # Return -1 if the player is not part of this game
        if not player in self.players.values():
            return -1

        # Creating a list of players (to be able to order them)
        # then sort it by points and then reversing the order so
        # that the first item is the first rank and so on
        player_list = list(self.players.values())
        player_list.sort(key=lambda x: x.points)
        player_list = player_list[::-1]

        # Rank is the index of the player_list. + 1 is added that the
        # first place is not 0 but 1
        rank = player_list.index(player) + 1

        return rank

    def get_player_count(self) -> int:
        """Returns the amount of players in this game"""
        return len(self.players)

    def get_team_count(self) -> int:
        """Returns the amount of teams in this game"""
        return len(self.teams)

    def get_player_index(self, player: Player) -> int:
        """Returns a number from 0 ... player count, do not use this number to
        identify the player but for thing where you need a count of players not
        skipping numbers. Like assinging colors, etc."""

        player_list = list(self.players.values())

        # Return -1 if the player is unknown
        if player not in player_list:
            return -1

        # Return the index of the player
        return player_list.index(player)
