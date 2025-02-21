from flask import Blueprint
from app.routes import handle_route_action
from app.controller import user

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/profile', methods=['GET'])
def user_profile():
    return handle_route_action(user.get_profile)    



@user_bp.route('/sign-up', methods=['POST'])
def sign_up():
    ret = user.signup(request.json)
    if ret is None:
        return "", HTTPStatus.UNAUTHORIZED
    else:
        return ret

@user_bp.route('/user/login', methods=['POST'])
def user_login():
    id_user = user.authenticate(request.json)
    if id_user is None:
        return "", HTTPStatus.UNAUTHORIZED
    else:
        return JwtManager.generate_access_token(id_user)



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
