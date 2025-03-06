from mysql.connector.errors import DatabaseError
import sys
import json
from http import HTTPStatus
from flask import Blueprint
import app.db as db

about_bp = Blueprint('about', __name__)

@about_bp.route('/hello', methods=['GET'])
def hello():
    try:
        api_version = json.load(open('version.json'))['version']
    except:
        print(f"Could not get API version.")
        api_version = 'N/A'

    try:
        query = "select VERSION from VERSION"
        result = db.execute_query(query, fetch=True)
        db_version = result[0][0]
        db_status = "Running"
    except DatabaseError:
        print(f"Could not connect to the database.")
        db_status = 'Down'
        db_version = 'N/A'

    body = {
        "API server status": "Running",
        "API version": api_version,
        "Database server status": db_status,
        "Database version": db_version
    }
    return body, HTTPStatus.OK
