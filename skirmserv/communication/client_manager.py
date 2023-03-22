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

import json

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
        self.clients = {} # key is socket_id, value is socketclient object
        self.spectators = {} # key is socket_id, value is spectator object
    
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
            old_client.reset()
            old_client.socket_id = socket_id
            self.clients.pop(old_socket_id)
            self.clients.update({socket_id: old_client})
            print("RE-Joined client: User: {0}, Socket: {1}".format(user, socket_id))
            return old_client

        # Else create a new SocketClient object, store it and return it
        new_client = SocketClient(socket_id, user, self.socketio)
        self.clients.update({socket_id: new_client})
        print("Joined client: User: {0}, Socket: {1}".format(user, socket_id))
        return new_client
    
    def _join_spectator(self, socket_id: str, gid: str) -> Spectator:
        game = GameManager.get_game(gid)

        current_spectator = self.spectators.get(socket_id, None)
        if current_spectator is not None:
            current_spectator.close()

        if game is not None:
            spectator = Spectator(socket_id, game, self.socketio)
            self.spectators.update({socket_id: spectator})

            print("Joined spectator: Socket: {0}, Game {1}".format(socket_id, game.gid))
            
            return spectator
    
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

            if socket_id is None or gid is None:
                return
            
            spectator = ClientManager.join_spectator(socket_id, gid)

            if spectator is None:
                data = json.dumps({"error": "Error spectating the specified game"})

        # Pass the callbacks to the socketio server
        self.socketio.on_event("join", socketio_join)
        self.socketio.on_event("message", socketio_message)
        self.socketio.on_event("spectate", socketio_spectate)