from flask import Blueprint, request
from flasgger import swag_from
from http import HTTPStatus
from app.routes.handler import handle_route_action
from app.controller import payee

payee_bp = Blueprint('payee', __name__)

@payee_bp.route('/payee/list', methods=['GET'])
@swag_from('../docs/payee/payee_list.yml')
def payee_list():
    return handle_route_action(payee.list)

@payee_bp.route('/payee/create', methods=['POST'])
@swag_from('../docs/payee/payee_create.yml')
def payee_create():
    return handle_route_action(payee.create, mode='create')

@payee_bp.route('/payee/delete', methods=['DELETE'])
@swag_from('../docs/payee/payee_delete.yml')
def payee_delete():
    return handle_route_action(payee.delete, mode='delete')
