from flask import Blueprint
from app.routes.handler import handle_route_action
from app.controller import transfer

transfer_bp = Blueprint('transfer', __name__)

@transfer_bp.route('/transfer/create', methods=['POST'])
def transfer_create():
    return handle_route_action(transfer.create, mode='create')
