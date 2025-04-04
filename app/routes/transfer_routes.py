from flask import Blueprint
from flasgger import swag_from
from app.routes.handler import handle_route_action
from app.controller import transfer

transfer_bp = Blueprint('transfer', __name__)

@transfer_bp.route('/transfer/create', methods=['POST'])
@swag_from('../docs/transaction/transfer_create.yml')
def transfer_create():
    return handle_route_action(transfer.create, mode='create')
