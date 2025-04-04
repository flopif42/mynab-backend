from flask import Blueprint, request
from flasgger import swag_from
from http import HTTPStatus
from app.routes.handler import handle_route_action
from app.controller import transaction

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/transaction/list', methods=['GET'])
@swag_from('../docs/transaction/transaction_list.yml')
def transaction_list():
    return handle_route_action(transaction.list)

@transaction_bp.route('/transaction/create', methods=['POST'])
@swag_from('../docs/transaction/transaction_create.yml')
def transaction_create():
    return handle_route_action(transaction.create, mode='create')

@transaction_bp.route('/transaction/delete', methods=['DELETE'])
@swag_from('../docs/transaction/transaction_delete.yml')
def transaction_delete():
    return handle_route_action(transaction.delete, mode='delete')
