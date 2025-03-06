from mysql.connector.errors import DatabaseError, ProgrammingError 
import sys
import json
from http import HTTPStatus
from flask import Blueprint
from app.sql_manager import SqlManager

about_bp = Blueprint('about', __name__)

@about_bp.route('/about', methods=['GET'])
def hello():
    db_version = 'N/A'
    db_status = "Running"

    try:
        api_version = json.load(open('version.json'))['version']
    except:
        print(f"Could not get API version.")
        api_version = 'N/A'
    try:
        query = "select VERSION from VERSION"
        result = SqlManager.execute_query(query, fetch=True)
        db_version = result[0][0]
    except IndexError:
        print(f"Could not retrieve the database version : no rows.")
    except ProgrammingError as err:
        print(f"There was a problem with a query : {err}.")
        db_status = 'Down'
    except DatabaseError:
        print(f"Could not connect to the database.")
        db_status = 'Down'
    body = {
        "API server status": "Running",
        "API version": api_version,
        "Database server status": db_status,
        "Database version": db_version
    }
    return body, HTTPStatus.OK
