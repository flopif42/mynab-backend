import json
import requests
import sys
from flask import Flask
from flask_cors import CORS, cross_origin
from http import HTTPStatus
import app
from app.jwt_manager import JwtManager
from app.sql_manager import SqlManager

def load_configuration():
    global _server_config

    try:
        _server_config = json.load(open('config.json'))
        JwtManager.set_config(_server_config['JwtParams'])
        SqlManager.set_config(_server_config['DatabaseParams'])
    except Exception as err:
        print(f"Could not load server configuration file. Exception: {err}")
        sys.exit(1)

app = app.create_app()
load_configuration()
CORS(app, **_server_config['CorsParams'])
