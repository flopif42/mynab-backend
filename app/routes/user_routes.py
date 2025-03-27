from flask import Blueprint, request
from http import HTTPStatus
from app.routes.handler import handle_route_action
from app.controller import user
from app.jwt_manager import JwtManager

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/login', methods=['POST'])
def user_login():
    id_user = user.login(request.json)
    if id_user is None:
        return "", HTTPStatus.UNAUTHORIZED
    return JwtManager.generate_access_token(id_user)

@user_bp.route('/user/profile', methods=['GET'])
def user_profile():
    return handle_route_action(user.get_profile)

@user_bp.route('/user/sign-up', methods=['POST'])
def sign_up():
    """
    New user registration.
    ---
    tags:
      - User
    parameters:
      - name: first_name
        in: query
        required: false
        type: string
        description: First name

      - name: last_name
        in: query
        required: false
        type: string
        description: Last name

      - name: email_address
        in: query
        required: true
        type: string
        description: Email address

      - name: passphrase_md5
        in: query
        required: true
        type: string
        description: MD5 encoded password

    responses:
      201:
        description: User was created successfully
      400:
        description: Missing required parameters or incorrect parameters
      500:
        description: Internal server error
    """
    try:
        if not request.is_json or 'email_address' not in request.json or 'passphrase_md5' not in request.json:
            raise ValueError
        if 'first_name' not in request.json:
            request.json['first_name'] = None
        if 'last_name' not in request.json:
            request.json['last_name'] = None
        print(request.json)
        ret = user.signup(request.json)
        if ret == 0: # OK
            return "", HTTPStatus.CREATED
        if ret == 1: # duplicate email_address
            return "", HTTPStatus.CONFLICT # 409
    except ValueError:
        return "", HTTPStatus.BAD_REQUEST
    except Exception as error:
        print(f"Exception in user_routes.sign_up() exception : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/user/check_email_available', methods=['GET'])
def check_email_available():
    """
    Checks if an email address is available for user creation.
    ---
    tags:
      - User
    parameters:
      - name: email_address
        in: query
        required: true
        type: string
        description: Email address to check

    responses:
      200:
        description: Email availability status
        examples:
          application/json:
            available: true
      400:
        description: Missing or invalid email parameter
      500:
        description: Internal server error
    """
    try:
        email_address = request.args.get("email_address")
        if not email_address:
            raise ValueError
        body_response = { "available" : user.is_available(email_address) }
        return body_response, HTTPStatus.OK
    except ValueError:
        return "", HTTPStatus.BAD_REQUEST
    except Exception as e:
        print(f"Exception in user_routes.check_email_available() exception : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR
