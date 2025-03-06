from flask import Blueprint

about_bp = Blueprint('about', __name__)

# -----------------------------------------------------------------------------
@about_bp.route('/hello', methods=['GET'])
def hello():
    version_fd = open('version.json')
    version = json.load(version_fd)['version']
    body = { "Server status": "Running", "Version": version }
    return body, HTTPStatus.OK
