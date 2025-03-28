from flask import Blueprint
from flasgger import swag_from
from app.routes.handler import handle_route_action
from app.controller import account

account_bp = Blueprint('account', __name__)

@account_bp.route('/account/create', methods=['POST'])
@swag_from('../docs/account/account_create.yml')
def account_create():
    try:
        return handle_route_action(account.create, create=True)
    except ValueError:
        return "", HTTPStatus.BAD_REQUEST
    except Exception as error:
        print(f"Exception in account_routes.account_create() : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@account_bp.route('/account/list', methods=['GET'])
def account_list():
    return handle_route_action(account.fetch_all)

@account_bp.route('/account/delete', methods=['POST'])
def account_delete():
    return handle_route_action(account.delete)

@account_bp.route('/account/toggle_status', methods=['POST'])
def account_toggle_status():
    return handle_route_action(account.toggle_status)
