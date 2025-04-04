from flask import Blueprint, request
from flasgger import swag_from
from http import HTTPStatus
from app.routes.handler import handle_route_action
from app.controller import user

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/login', methods=['POST'])
@swag_from('../docs/user/user_login.yml')
def user_login():
    return handle_route_action(user.login, auth_required=False)

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
    return handle_route_action(user.get_profile)
