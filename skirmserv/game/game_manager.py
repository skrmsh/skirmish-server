"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skirmserv.communication import SocketClient
    from skirmserv.models.user import UserModel

from skirmserv.game.player import Player
from skirmserv.game.game import Game
from skirmserv.gamemodes import available_gamemodes

from skirmserv.util.words import get_random_word_string

from logging import getLogger


class GameManager(object):
    instance = None

    @staticmethod
    def get_instance():
        """Returns the current instance of this class, if there is no
        instance of this class a new one is created and returned"""
        if GameManager.instance is not None:
            return GameManager.instance
        else:
            GameManager()
            return GameManager.instance

    def __init__(self):
        if GameManager.instance is not None:
            # Create a new instance only if there is no existing
            return
        GameManager.instance = self

        self.games = {}

    # Singleton wrapper methods
    @staticmethod
    def get_game(gid: str) -> Game:
        """Returns the game with the given gid"""
        return GameManager.get_instance()._get_game(gid)

    @staticmethod
    def create_game(gamemode: str, created_by: UserModel) -> str:
        """Creates a new Game instance with the given Gamemode and stores it
        returns the gameid (gid)"""
        return GameManager.get_instance()._create_game(gamemode, created_by)

    @staticmethod
    def start_game(gid: str, delay: int) -> None:
        """Startes the game with the given gid in `delay` seconds"""
        return GameManager.get_instance()._start_game(gid, delay)

    @staticmethod
    def join_game(game: Game, client: SocketClient) -> Player:
        """Joines this client to the game with the given gid. Returns the
        created player object"""
        return GameManager.get_instance()._join_game(game, client)

    @staticmethod
    def leave_game(client: SocketClient) -> None:
        """Removes this client and the associated player object from the
        currently joined game"""
        return GameManager.get_instance()._leave_game(client)

    @staticmethod
    def close_game(gid: str) -> None:
        """Closes the game with the given gid."""
        return GameManager.get_instance()._close_game(gid)

    # Singleton Wrapper wrapped methods

    def _get_game(self, gid: str) -> Game:
        """Returns the game with the given gid"""
        return self.games.get(gid, None)

    def _create_game(self, gamemode: str, created_by: UserModel) -> str:
        """Creates a new Game instance with the given Gamemode and stores it
        returns the gameid (gid)"""

        # Generate GameID
        gid = get_random_word_string()

        # Repeat as long as the gid is in use
        while gid in self.games.keys():
            gid = get_random_word_string()

        # Get Gamemode Class
        gm = available_gamemodes.get(gamemode, None)
        # Do not act if this gamemode is not avilable
        if gm is None:
            return

        # Create new game instance with given gamemode and generated gid
        game = Game(gm, gid, created_by)

        # Store the created instance
        self.games.update({gid: game})

        getLogger(__name__).info("Created new game: %s (GM: %s)", str(game), gamemode)

        return gid

    def _start_game(self, gid: str, delay: int) -> None:
        """Startes the game with the given gid in `delay` seconds"""
        raise NotImplementedError("Todo: Start Game")

    def _join_game(self, game: Game, client: SocketClient) -> Player:
        """Joines this client to the game with the given gid. Returns the
        created player object"""

        # If this client is already joined another game, leave it before
        if client.get_player() is not None:
            self._leave_game(client)

        # Create a new player instance
        player = Player(game, client)
        # Add it to the game
        game.add_player(player)
        # And associate the player to the client
        client.set_player(player)
        client.set_game(game)

        # Send udpated game and player data to the client
        client.trigger_action(client.ACTION_JOINED_GAME)
        client.update()

        getLogger(__name__).info("Joined player %s to game %s", str(player), str(game))

        return player

    def _leave_game(self, client: SocketClient) -> None:
        """Removes this client and the associated player object from the
        currently joined game"""

        # Get the associated player object and currently joined game
        player = client.get_player()
        game = client.get_game()

        # Remove the player from the game
        game.remove_player(player)

        # a left game looks for the client like a closed game
        client.trigger_action(client.ACTION_GAME_CLOSED)
        # Inform client about that leave
        client.update()

        # Clear game and player object from client
        client.game = None  # prevent the client to leave the game again
        client.reset()

        getLogger(__name__).info(
            "Removed player %s from game %s", str(player), str(game)
        )

        # if game has no players left -> close game
        if len(game.players) == 0:
            self._close_game(game.gid)

    def _close_game(self, gid: str) -> None:
        """Closes the game with the given gid."""

        # Get game by gid
        game = self._get_game(gid)

        if game is not None:
            # Close the game
            game.close()

            getLogger(__name__).info("Closed game %s", str(game))

            self.games.pop(game.gid)
            del game
