from flask import Blueprint, request
from http import HTTPStatus
from app.routes.handler import handle_route_action
from app.controller import user
from app.jwt_manager import JwtManager

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/login', methods=['POST'])
def user_login():
    """
    Logs the user in the app.
    ---
    tags:
      - User
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email_address:
              type: string
              description: The email address used as the login name
              example: scrooge@mail.com
            passphrase_md5:
              type: string
              description: MD5 encoded password
              example: abcdef1234567890abcdef1234567890
          required:
            - email_address
            - passphrase_md5

    responses:
      200:
        description: User successfully logged in
      401:
        description: Wrong credentials
      500:
        description: Internal server error
    """
    try:
        id_user = user.login(request.json)
        if not id_user:
            return "", HTTPStatus.UNAUTHORIZED
        return JwtManager.generate_access_token(id_user) # HTTP response with status code 200 and cookie set (no body)
    except Exception as error:
        print(f"Exception in user_routes.login() : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/user/sign-up', methods=['POST'])
def sign_up():
    """
    New user registration.
    ---
    tags:
      - User
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            first_name:
              type: string
              description: First name
              example: Scrooge
            last_name:
              type: string
              description: Last name
              example: McDuck
            email_address:
              type: string
              description: Email address
              example: scrooge@mail.com
            passphrase_md5:
              type: string
              description: MD5 encoded password
              example: abcdef1234567890abcdef1234567890
          required:
            - email_address
            - passphrase_md5

    responses:
      201:
        description: User was created successfully
      400:
        description: Missing required parameters or incorrect parameters
      409:
        description: Could not create the user because the email address is already used
      500:
        description: Internal server error
    """
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
        return { "available" : user.is_available(email_address) }, HTTPStatus.OK
    except ValueError:
        return "", HTTPStatus.BAD_REQUEST
    except Exception as e:
        print(f"Exception in user_routes.check_email_available() : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/user/profile', methods=['GET'])
def user_profile():
    """
    Gets information about a the logged in user.
    ---
    tags:
      - User

    responses:
      200:
        description: Information about the user
        examples:
          application/json:
            first_name: Scrooge
            last_name: McDuck
            email_address: scrooge@mail.com
      401:
        description: No user is logged in
      500:
        description: Internal server error
    """
    try:
        return handle_route_action(user.get_profile)
    except Exception as e:
        print(f"Exception in user_routes.user_profile() : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR
