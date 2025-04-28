from http import HTTPStatus
from flask import Flask, request, jsonify
from app.jwt_manager import JwtManager
import app.exceptions as ex

response_status = {
    'fetch': HTTPStatus.OK,
    'create': HTTPStatus.CREATED,
    ('delete', 'update'): HTTPStatus.NO_CONTENT,
    'InvalidParametersError': HTTPStatus.BAD_REQUEST,
    'UserInvalidCredentialsError': HTTPStatus.UNAUTHORIZED,
    ('AccountNotFoundError', 'PayeeNotFoundError', 'ParentCategoryNotFoundError', 'CategoryNotFoundError'): HTTPStatus.NOT_FOUND,
    ('AccountPermissionError', 'PayeePermissionError'): HTTPStatus.FORBIDDEN,
    ('AccountNotEmptyError', 'PayeeNotEmptyError', 'ParentCategoryNotEmptyError', 'CategoryNotEmptyError', 'UserMailAdressUnavailableError'): HTTPStatus.CONFLICT
}

def get_status_code(mode):
    if response_status.get(mode):
        return response_status.get(mode)
    for key in response_status.keys():
        if isinstance(key, tuple) and mode in key:
            return response_status.get(key)
    return HTTPStatus.INTERNAL_SERVER_ERROR

def handle_route_action(action, mode='fetch', auth_required=True):
    if auth_required and not JwtManager.check_token_valid(request):
        return '', HTTPStatus.UNAUTHORIZED
    try:
        id_user = JwtManager.get_id_user_from_token(request) if auth_required else None
        result = action(id_user, request)
        if mode in ('login', 'logout'):
            return result
        response_body = '' if result is None else jsonify(result)
        return response_body, get_status_code(mode)
    except ex.MyOperationError as error:
        return { "error": error.error_message }, get_status_code(type(error).__name__)
    except Exception as error:
        print(f"Exception in handle_route_action() : {type(error).__name__} - {error}")
        return '', HTTPStatus.INTERNAL_SERVER_ERROR
