from flask import Blueprint, request
from flasgger import swag_from
from http import HTTPStatus
from app.routes.handler import handle_route_action
from app.controller import payee
from app.controller.payee import PayeeOperationError

payee_bp = Blueprint('payee', __name__)

@payee_bp.route('/payee/create', methods=['POST'])
@swag_from('../docs/payee/payee_create.yml')
def payee_create():
    try:
        if not request.is_json or 'payee_name' not in request.json:
            raise ValueError
        return handle_route_action(payee.create, create=True)
    except ValueError:
        return "", HTTPStatus.BAD_REQUEST
    except Exception as error:
        print(f"Exception in payee_routes.payee_create() : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@payee_bp.route('/payee/delete', methods=['DELETE'])
@swag_from('../docs/payee/payee_delete.yml')
def payee_delete():
    try:
        if not request.is_json or 'id_payee' not in request.json:
            raise PayeeOperationError(HTTPStatus.BAD_REQUEST, "The parameter ID payee is required.")
        return handle_route_action(payee.delete, delete=True)
    except ValueError:
        return "", HTTPStatus.BAD_REQUEST
    except PayeeOperationError as error:
        return { "error": error.args[1] }, error.args[0]
    except Exception as error:
        print(f"Exception in payee_routes.payee_delete() : {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@payee_bp.route('/payee/list', methods=['GET'])
@swag_from('../docs/payee/payee_list.yml')
def payee_list():
    return handle_route_action(payee.list)
