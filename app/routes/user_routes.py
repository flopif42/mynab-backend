import flask
from http import HTTPStatus
from app.routes.handler import handle_route_action
from app.controller import user
from app.jwt import JwtManager

user_bp = flask.Blueprint('user', __name__)

@user_bp.route('/user/login', methods=['POST'])
def user_login():
    id_user = user.login(flask.request.json)
    if id_user is None:
        return "", HTTPStatus.UNAUTHORIZED
    return JwtManager.generate_access_token(id_user)

@user_bp.route('/user/profile', methods=['GET'])
def user_profile():
    return handle_route_action(user.get_profile)

@user_bp.route('/user/sign-up', methods=['POST'])
def sign_up():
    ret = user.signup(flask.request.json)
    if ret == 403: # duplicate email_address
        return "", HTTPStatus.FORBIDDEN
    if ret == 400: # other error
        return "", HTTPStatus.BAD_REQUEST
    return "", HTTPStatus.OK

@user_bp.route('/user/available', methods=['POST'])
def available():
    ret = user.is_available(flask.request.json)
    if ret == 1:
        return { "available" : "yes" }, HTTPStatus.OK
    if ret == 0:
        return { "available" : "no" }, HTTPStatus.OK
    if ret == -1:
        return "", HTTPStatus.BAD_REQUEST
