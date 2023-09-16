"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from flask import Flask
from flask_socketio import SocketIO
from flask_restful import Api

from flask import render_template

from logging.config import dictConfig

from flasgger import Swagger, swag_from

# Creating Flask app & SocketIO server
app = Flask(__name__)
app.config.from_envvar("SKIRMSERV_CFG")
socketio = SocketIO(app, cors_allowed_origins="*")  # Socket IO websocket app
flask_api = Api(app)  # Restful api

SWAGGER_TEMPLATE = {
    "securityDefinitions": {
        "AccessTokenHeader": {
            "type": "apiKey",
            "name": "x-access-token",
            "in": "header",
        }
    }
}

swag = Swagger(app, template=SWAGGER_TEMPLATE)

# Logger config
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": app.config.get("LOGGING_LEVEL"), "handlers": ["wsgi"]},
    }
)

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
from skirmserv.api.game import GamesAPI
from skirmserv.api.team import TeamAPI
from skirmserv.api.gamemode import GamemodeAPI

flask_api.add_resource(UserAPI, "/user")
flask_api.add_resource(AuthAPI, "/auth")
flask_api.add_resource(GameAPI, "/game/<string:gid>")
flask_api.add_resource(TeamAPI, "/team/<string:gid>/<int:tid>")
flask_api.add_resource(GamesAPI, "/games")
flask_api.add_resource(GamemodeAPI, "/gamemode")
app.logger.info("Welcome! API + WS up and running.")


# Test Route serving SocketIO test client
@app.route("/siotest")
def socketio_test():
    return render_template("socketio_test.html")
