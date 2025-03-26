from flask import Blueprint
from app.routes.handler import handle_route_action
from app.controller import account

account_bp = Blueprint('account', __name__)

@account_bp.route('/account/list', methods=['GET'])
def account_list():
    return handle_route_action(account.fetch_all)

@account_bp.route('/account/create', methods=['POST'])
def account_create():
    return handle_route_action(account.create, create=True)

@account_bp.route('/account/delete', methods=['POST'])
def account_delete():
    return handle_route_action(account.delete)

@account_bp.route('/account/toggle_status', methods=['POST'])
def account_toggle_status():
    return handle_route_action(account.toggle_status)
