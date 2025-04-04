from flask import Blueprint, request
from flasgger import swag_from
from http import HTTPStatus
from app.routes.handler import handle_route_action
from app.controller import user
from app.jwt_manager import JwtManager

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/login', methods=['POST'])
@swag_from('../docs/user/user_login.yml')
def user_login():
    try:
        id_user = user.login(request.json)
        if not id_user:
            return "", HTTPStatus.UNAUTHORIZED
        return JwtManager.generate_access_token(id_user) # HTTP response with status code 200 and cookie set (no body)
    except Exception as error:
        print(f"Exception in user_routes.login() : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/user/sign-up', methods=['POST'])
@swag_from('../docs/user/signup.yml')
def sign_up():
    return handle_route_action(user.signup, auth_required=False)

@user_bp.route('/user/check_email_available', methods=['GET'])
@swag_from('../docs/user/check_email_available.yml')
def check_email_available():
    return handle_route_action(user.is_email_available, auth_required=False)

@user_bp.route('/user/profile', methods=['GET'])
@swag_from('../docs/user/user_profile.yml')
def user_profile():
    return handle_route_action(user.get_profile, auth_required=False)
