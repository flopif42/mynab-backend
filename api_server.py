import json
import requests
import sys
from flask import Flask
from flask_cors import CORS, cross_origin
from http import HTTPStatus
import app
from app.jwt import JwtManager
from app.db import DbPool

def load_configuration():
    global _server_config

    try:
        _server_config = json.load(open('config.json'))
        JwtManager._config = server_config['JwtParams']
        DbPool._config = server_config['DatabaseParams']
    except Exception as err:
        print(f"Could not load server configuration file. Exception: {err}")
        sys.exit(1)

app = app.create_app()
load_configuration()
CORS(app, **_server_config['CorsParams'])

# -----------------------------------------------------------------------------
@app.route('/hello', methods=['GET'])
def hello():
    version_fd = open('version.json')
    version = json.load(version_fd)['version']
    body = { "Server status": "Running", "Version": version }
    return body, HTTPStatus.OK
