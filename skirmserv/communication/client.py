"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skirmserv.models.user import UserModel

from flask import request
from flask_socketio import SocketIO  # Just for typing
import json

from skirmserv.game.player import Player
from skirmserv.game.game import Game
from skirmserv.game.team import Team
from skirmserv.game.game_manager import GameManager


class SocketClient(object):
    # Action codes
    ACTION_KEEP_ALIVE = 0
    ACTION_TIMESYNC = 1
    ACTION_JOIN_GAME = 2
    ACTION_JOINED_GAME = 3
    ACTION_LEAVE_GAME = 4
    ACTION_GAME_CLOSED = 5
    ACTION_GOT_HIT = 6
    ACTION_SEND_SHOT = 7
    ACTION_HIT_VALID = 8
    ACTION_SHOT_HIT = 9
    ACTION_ADD_AMMO = 10
    ACTION_JOINED_SERVER = 11
    ACTION_FULL_DATA_UPDATE = 12
    ACTION_SERVER_JOIN_DENIED = 13
    ACTION_INVALID_GAME = 14

    def __init__(self, socket_id: str, user: UserModel, socketio: SocketIO):
        self.socket_id = socket_id
        self.user = user
        self.socketio = socketio

        self.current_actions = set()
        self.current_data = {}

        self.player = None
        self.game = None
        self.team = None

        # Dicts to store the last sent player/game/team data. Used to
        # get the difference and send only changed fields (except some
        # fields that are always set)
        self.last_sent_pgt_data = {}

    def reset(self) -> None:
        """Resets this client to initial state"""
        self.current_actions = set()
        self.current_data = {}
        self.last_sent_pgt_data = {}
        self.game = None
        self.player = None
        self.team = None

    def get_player(self) -> Player:
        """Returns the associated player object"""
        return self.player

    def clear_player(self) -> None:
        """Clears the associated player object"""
        self.player = None

    def set_player(self, player: Player) -> None:
        """Sets the associated player object"""
        self.player = player

    def get_game(self) -> Game:
        """Returns the currently joined game"""
        return self.game

    def clear_game(self) -> None:
        """Clears the currently joined game"""
        self.game = None

    def set_game(self, game: Game) -> None:
        """Sets the currently joined game"""
        self.game = game

    def trigger_action(self, code: int, **param: dict) -> None:
        """Triggers the given action on the client with the given parameters.
        The parameter are not checked on server side. The trigger is send when
        client.update is called the next time"""
        self.current_actions.add(code)
        self.current_data.update(param)

    def set_field(self, field_data: dict) -> None:
        """Sets a field, will be send next time update is called"""
        self.current_data.update(field_data)

    def update(self, full=False):
        """Sends this client a update with all triggered actions and data"""

        # Create data object with actions
        data = {"a": list(self.current_actions)}
        # and add (parameter) data
        data.update(self.current_data)

        # Create pgt data (player/game/team)
        new_pgt = {}

        # Add fields from player object if available
        if self.player is not None:
            new_pgt.update(self.player.get_pgt_data())

        # Add fields from game object if available
        if self.game is not None:
            new_pgt.update(self.game.get_pgt_data())

        # Add fields from team object if available
        if self.team is not None:
            # TODO: implement team data
            new_pgt.update(self.team.get_pgt_data())

        # if not full data is requested
        if not full:
            # get difference between last and new pgt data
            pgt_diff = {}

            # Todo: This is probably more elegant possible
            for key in new_pgt:
                old_value = self.last_sent_pgt_data.get(key, None)
                new_value = new_pgt.get(key, None)
                if old_value != new_value:
                    pgt_diff.update({key: new_value})

            self.last_sent_pgt_data = new_pgt

            # Update data (which will be send) with all changed fields
            data.update(pgt_diff)

        # If full data is requested
        else:
            # Set last sent data that diff works next time
            self.last_sent_pgt_data = new_pgt
            # update data with all fields
            data.update(new_pgt)

        # Clear current actions and (param) data
        self.current_actions.clear()
        self.current_data.clear()

        # Send data to the socket
        self.send(data)

    def send(self, data: dict, event="message") -> None:
        """Sends the given data dictionary (in skirmish format) to the client"""
        if self.socket_id is not None:
            data = json.dumps(data)
            self.socketio.emit(event, data, to=self.socket_id)

    def on_receive(self, data: dict) -> None:
        """Should be called when from this client some data is received on the
        message event."""

        # Protocol requires that "a" is always given but just using an empty
        # list of actions when there is not field "a" in the received data
        actions = data.get("a", [])

        for action in actions:
            if action == SocketClient.ACTION_JOIN_GAME:
                self._on_join_game(data)
            elif action == SocketClient.ACTION_LEAVE_GAME:
                self._on_leave_game(data)
            elif action == SocketClient.ACTION_GOT_HIT:
                self._on_got_hit(data)
            elif action == SocketClient.ACTION_SEND_SHOT:
                self._on_send_shot(data)
            elif action == SocketClient.ACTION_FULL_DATA_UPDATE:
                self.update(full=True)

    def _on_join_game(self, data):
        """Join Game Event triggered by client"""

        # Get Parameters
        gid = data.get("gid", None)

        # Do not act if gid is not available
        if gid is None:
            self.trigger_action(SocketClient.ACTION_INVALID_GAME)
            self.update()
            return

        # Get game by gid
        game = GameManager.get_game(gid)
        # Do not act if this game is unknown
        if game is None:
            self.trigger_action(SocketClient.ACTION_INVALID_GAME)
            self.update()
            return

        # Join to the game with the given gid
        GameManager.join_game(game, self)

    def _on_leave_game(self, data):
        """Leave Game Event triggered by client"""
        GameManager.leave_game(self)

        self.reset()

    def _on_got_hit(self, data):
        """Got Hit Event triggered by client"""
        if self.player is not None:
            # Get pid and sid fields
            pid = data.get("pid", None)
            sid = data.get("sid", None)

            # do not act on missing fields
            if pid is None or sid is None:
                return

            # Trigger got_hit method from associated player
            self.player.got_hit(pid, sid)

    def _on_send_shot(self, data):
        """Send Shot event triggered by client"""
        if self.player is not None:
            # Get sid field
            sid = data.get("sid", None)

            # do not act on missing field
            if sid is None:
                return

            # Trigger send_shot method from associated player
            self.player.send_shot(sid)

    def close(self):
        """Called when the websocket connection was closed"""
        self._on_leave_game(None)
