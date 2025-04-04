from flask import Flask, request, jsonify
from app.jwt_manager import JwtManager
from http import HTTPStatus
from app.exceptions import OperationError

response_status = {
    'default': HTTPStatus.OK,
    'create': HTTPStatus.CREATED,
    'delete': HTTPStatus.NO_CONTENT,
    'update': HTTPStatus.NO_CONTENT,
    'server_error': HTTPStatus.INTERNAL_SERVER_ERROR,
    'unauthorized': HTTPStatus.UNAUTHORIZED 
}

def handle_route_action(action, mode='default', auth_required=True):
    response_body = ''
    if auth_required and not JwtManager.check_token_valid(request):
        return response_body, response_status['unauthorized']
    try:
        id_user = JwtManager.get_id_user_from_token(request) if auth_required else None
        result = action(id_user, request)
        if result:
            response_body = jsonify(result)
        return response_body, response_status[mode]
    except OperationError as error:
        print(f"OperationError in handle_route_action() : {type(error).__name__} - {error}")
        print(error.get_status())
        return { "error": error.get_status() }, error.get_message()
    except Exception as error:
        print(f"Exception in handle_route_action() : {type(error).__name__} - {error}")
        return response_body, response_status['server_error']
