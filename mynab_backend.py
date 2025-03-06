import json
import sys
import flask_cors
import app
from app.jwt_manager import JwtManager
from app.sql_manager import SqlManager

mynab_app = app.create_app()
try:
    server_config = json.load(open('config.json'))
    JwtManager.set_config(server_config['JwtParams'])
    SqlManager.set_config(server_config['DatabaseParams'])
    flask_cors.CORS(mynab_app, **server_config['CorsParams'])
except Exception as err:
    print(f"Could not load server configuration file. Exception: {err}")
    sys.exit(1)
