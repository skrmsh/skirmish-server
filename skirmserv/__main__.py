"""
Skirmish Server

Copyright (C) 2022 Ole Lange
"""

from skirmserv import socketio, app

socketio.run(app, host="::", port=8081, debug=True, use_reloader=True, log_output=True)
