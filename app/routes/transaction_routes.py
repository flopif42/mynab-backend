from flask import Blueprint, request
from app.routes.handler import handle_route_action
from app.controller import transaction

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/transaction/list', methods=['POST'])
def transaction_list():
    return handle_route_action(transaction.fetch_all)

@transaction_bp.route('/transaction/create', methods=['POST'])
def transaction_create():
    return handle_route_action(transaction.create, create=True)

@transaction_bp.route('/transaction/delete', methods=['POST'])
def transaction_delete():
    return handle_route_action(transaction.delete)
