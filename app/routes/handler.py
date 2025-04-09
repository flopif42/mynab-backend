from http import HTTPStatus
from flask import Flask, request, jsonify
from app.jwt_manager import JwtManager
import app.exceptions as ex

response_status = {
    'fetch': HTTPStatus.OK,
    'create': HTTPStatus.CREATED,
    'delete': HTTPStatus.NO_CONTENT,
    'update': HTTPStatus.NO_CONTENT,
    'AccountNotFoundError': HTTPStatus.NOT_FOUND,
    'AccountPermissionError': HTTPStatus.FORBIDDEN,
    'AccountNotEmptyError': HTTPStatus.CONFLICT
}

def handle_route_action(action, mode='fetch', auth_required=True):
    response_body = ''
    if auth_required and not JwtManager.check_token_valid(request):
        return response_body, HTTPStatus.UNAUTHORIZED
    try:
        id_user = JwtManager.get_id_user_from_token(request) if auth_required else None
        result = action(id_user, request)
        if result:
            response_body = jsonify(result)
        return response_body, response_status[mode]
    except ex.AccountOperationError as error:
        return { "error": error.error_message }, response_status[type(error).__name__]
    except ex.OperationError as error:
        return { "error": error.message }, error.status
    except Exception as error:
        print(f"Exception in handle_route_action() : {type(error).__name__} - {error}")
        return response_body, HTTPStatus.INTERNAL_SERVER_ERROR
