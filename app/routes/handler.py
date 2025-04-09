from flask import Flask, request, jsonify
from app.jwt_manager import JwtManager
from http import HTTPStatus
from app.exceptions import OperationError, AccountNotExistError, AccountWrongOwnerError, AccountNotEmptyError

response_status = {
    'fetch': HTTPStatus.OK,
    'create': HTTPStatus.CREATED,
    'delete': HTTPStatus.NO_CONTENT,
    'update': HTTPStatus.NO_CONTENT
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
    except AccountNotExistError as error:
        return { "error": str(error) }, HTTPStatus.NOT_FOUND
    except AccountWrongOwnerError as error:
        return { "error": error }, HTTPStatus.FORBIDDEN
    except AccountNotEmptyError as error:
        return { "error": error }, HTTPStatus.CONFLICT
    except OperationError as error:
        return { "error": error.message }, error.status
    except Exception as error:
        print(f"Exception in handle_route_action() : {type(error).__name__} - {error}")
        return response_body, HTTPStatus.INTERNAL_SERVER_ERROR
