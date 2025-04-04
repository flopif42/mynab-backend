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
    try:
        if not request.is_json or 'email_address' not in request.json or 'passphrase_md5' not in request.json:
            raise ValueError
        user.signup(request.json)
        return "", HTTPStatus.CREATED
    except ValueError:
        return "", HTTPStatus.BAD_REQUEST
    except RuntimeError as integrity_error:
        print(integrity_error)
        return "", HTTPStatus.CONFLICT # 409
    except Exception as error:
        print(f"Exception in user_routes.sign_up() : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/user/check_email_available', methods=['GET'])
@swag_from('../docs/user/check_email_available.yml')
def check_email_available():
    try:
        email_address = request.args.get("email_address")
        if not email_address:
            raise ValueError
        return { "available" : user.is_available(email_address) }, HTTPStatus.OK
    except ValueError:
        return "", HTTPStatus.BAD_REQUEST
    except Exception as error:
        print(f"Exception in user_routes.check_email_available() : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/user/profile', methods=['GET'])
@swag_from('../docs/user/user_profile.yml')
def user_profile():
    return handle_route_action(user.get_profile)
