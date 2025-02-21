import flask
import http
from app.routes import handle_route_action
from app.controller import user
from app.jwt import JwtManager

user_bp = flask.Blueprint('user', __name__)

@user_bp.route('/user/login', methods=['POST'])
def user_login():
    id_user = user.login(flask.request.json)
    if id_user is None:
        return "", http.HTTPStatus.UNAUTHORIZED
    return JwtManager.generate_access_token(id_user)

@user_bp.route('/user/profile', methods=['GET'])
def user_profile():
    return handle_route_action(user.get_profile)

@user_bp.route('/user/sign-up', methods=['POST'])
def sign_up():
    user.signup(flask.request.json)
    return "Test in progress", 500

@user_bp.route('/user/logout', methods=['POST'])
def user_logout():
    data = {}
    access_token_valid = JwtManager.check_token_valid(request)
    if access_token_valid:
        id_user = JwtManager.get_id_user_from_token(request)
        data['logout'] = "Success"
        return data, HTTPStatus.OK
    else:
        return "", HTTPStatus.UNAUTHORIZED
