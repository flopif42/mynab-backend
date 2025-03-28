from flask import Blueprint, request
from flasgger import swag_from
from http import HTTPStatus
from app.routes.handler import handle_route_action
from app.controller import account, AccountOperationError

account_bp = Blueprint('account', __name__)

@account_bp.route('/account/list', methods=['GET'])
def account_list():
    return handle_route_action(account.fetch_all)

@account_bp.route('/account/delete', methods=['DELETE'])
@swag_from('../docs/account/account_delete.yml')
def account_delete():
    try:
        if not request.is_json or 'id_account' not in request.json:
            raise ValueError(400, "The parameter ID account is required.")
        return handle_route_action(account.delete, delete=True)
    except AccountOperationError as error:
        return { "error": error.args[1] }, error.args[0]
    except Exception as error:
        print(f"Exception in account_routes.account_delete() : {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@account_bp.route('/account/toggle_status', methods=['POST'])
def account_toggle_status():
    return handle_route_action(account.toggle_status)

@account_bp.route('/account/create', methods=['POST'])
@swag_from('../docs/account/account_create.yml')
def account_create():
    try:
        if not request.is_json or 'account_name' not in request.json or 'account_type' not in request.json:
            raise ValueError
        return handle_route_action(account.create, create=True)
    except ValueError:
        return "", HTTPStatus.BAD_REQUEST
    except Exception as error:
        print(f"Exception in account_routes.account_create() : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR
