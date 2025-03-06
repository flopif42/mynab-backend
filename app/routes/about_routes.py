import sys
import json
from http import HTTPStatus
from flask import Blueprint

about_bp = Blueprint('about', __name__)

@about_bp.route('/hello', methods=['GET'])
def hello():
    try:
        version = json.load(open('version.json'))['version']
        body = { "Server status": "Running", "Version": version }
        return body, HTTPStatus.OK
    except Exception as err:
        print(f"Could not load version file. Exception: {err}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR
