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

def handle_route_action(action, mode='default'):
    response_body = ''
    if not JwtManager.check_token_valid(request):
        mode = 'unauthorized'
    else:
        try:
            id_user = JwtManager.get_id_user_from_token(request)
            result = action(id_user, request)
            if result:
                response_body = jsonify(result)
        except OperationError as error:
            return { "error": error.args[1] }, error.args[0]
        except Exception as error:
            print(f"Exception in handle_route_action() : {type(error).__name__} - {error}")
            mode = 'server_error'
    return response_body, success_response_status[mode]
