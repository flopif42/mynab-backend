from flask import Flask, request, jsonify
from app.jwt_manager import JwtManager
from http import HTTPStatus

def handle_route_action(action, create=False):
    if not JwtManager.check_token_valid(request):
        return "", HTTPStatus.UNAUTHORIZED
    try:
        id_user = JwtManager.get_id_user_from_token(request)
        result = action(id_user, request.json if request.is_json else None)
        responseBody = "" if result is None else jsonify(result)
        responseStatus = HTTPStatus.CREATED if create else HTTPStatus.OK
        return responseBody, responseStatus
    except Exception as error:
        print(f"Exception in handle_route_action() : {error}")
        raise error
