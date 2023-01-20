"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from flask import Flask
from flask_socketio import SocketIO
from flask_restful import Api

from flask import render_template

# Creating Flask app & SocketIO server
app = Flask(__name__)
app.config.from_envvar("SKIRMSERV_CFG")
socketio = SocketIO(app, cors_allowed_origins='*') # Socket IO websocket app
flask_api = Api(app) # Restful api

# Initialize the Database connection
with app.app_context():
    from skirmserv.models import Database
    Database()

# Create ClientManager and set SocketIO server to receive and send messages
from skirmserv.communication.client_manager import ClientManager
ClientManager.set_socketio(socketio)

# Register Resources to the API
from skirmserv.api.user import UserAPI
from skirmserv.api.user import AuthAPI
from skirmserv.api.game import GameAPI
flask_api.add_resource(UserAPI, "/user")
flask_api.add_resource(AuthAPI, "/auth")
flask_api.add_resource(GameAPI, "/game/<string:gid>")

# Test Route serving SocketIO test client
@app.route("/siotest")
def socketio_test():
    return render_template("socketio_test.html")