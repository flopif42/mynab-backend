from flask import Blueprint
from app.handler import handle_route_action
from app.controller import payee

payee_bp = Blueprint('payee', __name__)

@payee_bp.route('/payee/list', methods=['GET'])
def payee_list():
    return handle_route_action(payee.fetch_all)

@payee_bp.route('/payee/create', methods=['POST'])
def payee_create():
    return handle_route_action(payee.create)

@payee_bp.route('/payee/delete', methods=['POST'])
def payee_delete():
    return handle_route_action(payee.delete)
