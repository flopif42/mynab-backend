from flask import Blueprint
from flasgger import swag_from
from app.routes.handler import handle_route_action
from app.controller import account

account_bp = Blueprint('account', __name__)

@account_bp.route('/account/list', methods=['GET'])
@swag_from('../docs/account/account_list.yml')
def account_list():
    return handle_route_action(account.list)

@account_bp.route('/account/create', methods=['POST'])
@swag_from('../docs/account/account_create.yml')
def account_create():
    return handle_route_action(account.create, mode='create')

@account_bp.route('/account/delete', methods=['DELETE'])
@swag_from('../docs/account/account_delete.yml')
def account_delete():
    return handle_route_action(account.delete, mode='delete')

@account_bp.route('/account/set_status', methods=['PUT'])
@swag_from('../docs/account/account_set_status.yml')
def set_status():
    return handle_route_action(account.set_status, mode='update')
