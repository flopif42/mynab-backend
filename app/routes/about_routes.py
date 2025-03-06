import sys
import json
from http import HTTPStatus
from flask import Blueprint
import app.db as db

about_bp = Blueprint('about', __name__)

@about_bp.route('/hello', methods=['GET'])
def hello():
    try:
        query = "select VERSION from VERSION"
        result = db.execute_query(query, fetch=True)
        db_version = result[0][0]
        api_version = json.load(open('version.json'))['version']
        body = {
            "API server status": "Running",
            "API version": api_version,
            "Database server status": db_status,
            "Database version": db_version
        }
        return body, HTTPStatus.OK
    except Exception as err:
        print(f"Could not load version file. Exception: {err}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR
