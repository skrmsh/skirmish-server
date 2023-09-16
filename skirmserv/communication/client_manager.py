"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from skirmserv.communication import SocketClient
from skirmserv.communication.spectator import Spectator
from skirmserv.models.user import UserModel

from skirmserv.game.game_manager import GameManager

from flask import request
from flask import current_app
from flask_socketio import SocketIO

import time
import json
from logging import getLogger


class ClientManager(object):
    instance = None

    @staticmethod
    def get_instance():
        """Returns the current instance of this class, if there is no
        instance of this class a new one is created and returned"""
        if ClientManager.instance is not None:
            return ClientManager.instance
        else:
            ClientManager()
            return ClientManager.instance

    def __init__(self):
        if ClientManager.instance is not None:
            # Create a new instance only if there is no existing
            return
        ClientManager.instance = self

        self.socketio = None
        self.clients = {}  # key is socket_id, value is socketclient object
        self.spectators = {}  # key is socket_id, value is spectator object

    # Singleton Wrapper methods
    @staticmethod
    def get_client(socket_id):
        """Returns the client associated with this socket."""
        return ClientManager.get_instance()._get_client(socket_id)

    @staticmethod
    def set_socketio(socketio: SocketIO) -> None:
        """Set socketio server"""
        return ClientManager.get_instance()._set_socketio(socketio)

    @staticmethod
    def join_client(access_token: str, socket_id: str) -> SocketClient:
        """Creates a new SocketClient object and stores it. If there is already
        a client with the given access token from another socket, the socket is
        replaced with the new one."""
        return ClientManager.get_instance()._join_client(access_token, socket_id)

    @staticmethod
    def join_spectator(socket_id: str, gid: str) -> Spectator:
        """Creates a new Spectator object for the given game and stores it."""
        return ClientManager.get_instance()._join_spectator(socket_id, gid)

    @staticmethod
    def get_spectator(socket_id: str) -> Spectator:
        """Returns the spectator object from this socket"""
        return ClientManager.get_instance()._get_spectator(socket_id)

    # Singleton Wrapper wrapped methods
    def _get_client(self, socket_id):
        """Returns the client associated with this socket."""
        return self.clients.get(socket_id, None)

    def _join_client(self, access_token: str, socket_id: str) -> SocketClient:
        """Creates a new SocketClient object and stores it. If there is already
        a client with the given access token from another socket, the socket is
        replaced with the new one."""

        user = UserModel.authenticate_by_token(access_token)
        if user is None:
            return

        # Check if there is already a client with the given access_token.
        # If so, the old socket id is stored.
        old_socket_id = None
        for existing_socket_id in self.clients:
            client = self.clients[existing_socket_id]

            # If there is already a client from another socket from this user
            if client.user.id == user.id:
                old_socket_id = existing_socket_id
                break

            # If there is a connection from this socket from other user
            if existing_socket_id == socket_id:
                # delete the existing client and create a new one later on
                del client

        # Replace if there is a old connection and return the client object
        if old_socket_id is not None:
            old_client = self.clients[old_socket_id]
            # if the last disconnect event was more than 10 minutes ago
            # the client will be reset
            if (
                old_client.connection_closed > 0
                and time.time() - old_client.connection_closed > 600
            ):
                old_client.reset()
            old_client.connection_closed = 0
            old_client.socket_id = socket_id
            self.clients.pop(old_socket_id)
            self.clients.update({socket_id: old_client})

            # Sending full data to the client if currently ingame
            if old_client.game is not None:
                old_client.trigger_action(SocketClient.ACTION_FULL_DATA_UPDATE)
                old_client.update(full=True)

            getLogger(__name__).info("Re-Joined client: %s", str(old_client))

            return old_client

        # Else create a new SocketClient object, store it and return it
        new_client = SocketClient(socket_id, user, self.socketio)
        self.clients.update({socket_id: new_client})
        getLogger(__name__).info("Joined client: %s", str(new_client))
        return new_client

    def _join_spectator(self, socket_id: str, gid: str) -> Spectator:
        game = GameManager.get_game(gid)

        current_spectator = self.spectators.get(socket_id, None)
        if current_spectator is not None:
            current_spectator.close()

        if game is not None:
            spectator = Spectator(socket_id, game, self.socketio)
            self.spectators.update({socket_id: spectator})

            getLogger(__name__).info("Joined spectator: %s", str(spectator))

            return spectator

    def _get_spectator(self, socket_id: str) -> Spectator:
        """Returns the spectator object assigned to the specified socket_id"""
        return self.spectators.get(socket_id, None)

    def _set_socketio(self, socketio: SocketIO) -> None:
        """Set socketio server"""
        self.socketio = socketio

        # Callback for messages on "join" event
        def socketio_join(data: dict) -> None:
            # Get access_token & socketid
            socket_id = request.sid
            access_token = data.get("access_token", None)

            # Do nothing on invalid requests
            if socket_id is None or access_token is None:
                return

            client = ClientManager.join_client(access_token, socket_id)

            if client is not None:
                # Sending "joined server" event
                client.trigger_action(client.ACTION_JOINED_SERVER)
                client.update()
            else:
                # Sending "join denied" event
                data = json.dumps({"a": [SocketClient.ACTION_SERVER_JOIN_DENIED]})
                self.socketio.emit("message", data, to=socket_id)

        # Callback for messages on "message" event
        def socketio_message(data: dict) -> None:
            # Only act when received data is json
            if type(data) != dict:
                return

            # Get client by socket id
            client = ClientManager.get_client(request.sid)

            # If the client is existing, call the receive function of the
            # specific client with the received data.
            if client is not None:
                client.on_receive(data)

        # Callback for messages on "spectate" event
        def socketio_spectate(data: dict) -> None:
            socket_id = request.sid
            gid = data.get("gid", None)
            close = data.get("close", None)

            if socket_id is None or (gid is None and close is None):
                return

            spectator = ClientManager.get_spectator(socket_id)

            if close is not None and spectator is not None:
                spectator.close()

            if gid is not None:
                spectator = ClientManager.join_spectator(socket_id, gid)

        # Callback for disconnect socket event
        def on_socket_disconnect() -> None:
            sid = request.sid

            client = ClientManager.get_client(sid)
            if client is not None:
                client.close()

            spectator = ClientManager.get_spectator(sid)
            if spectator is not None:
                spectator.close()
                ClientManager.get_instance().spectators.pop(sid)

            getLogger(__name__).debug("Socket %s closed", sid)

        # Pass the callbacks to the socketio server
        self.socketio.on_event("join", socketio_join)
        self.socketio.on_event("message", socketio_message)
        self.socketio.on_event("spectate", socketio_spectate)

        self.socketio.on_event("disconnect", on_socket_disconnect)
