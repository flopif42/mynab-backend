from flask import Blueprint
from app.routes.handler import handle_route_action
from app.controller import account

account_bp = Blueprint('account', __name__)

@account_bp.route('/account/list', methods=['GET'])
def account_list():
    return handle_route_action(account.fetch_all)

@account_bp.route('/account/create', methods=['POST'])
def account_create():
    """
    Adds a new account.
    ---
    tags:
      - Account
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            account_name:
              type: string
              description: The account name
              example: Checking
            account_type:
              type: number
              description: The type of account (1\: on-budget, 2\: off-budget)
              example: 1
          required:
            - account_name
            - account_type
    responses:
      201:
        description: Account was created successfully
      400:
        description: Missing required parameters or incorrect parameters
      401:
        description: No user is logged in
      500:
        description: Internal server error
    """
    return handle_route_action(account.create, create=True)

@account_bp.route('/account/delete', methods=['POST'])
def account_delete():
    return handle_route_action(account.delete)

@account_bp.route('/account/toggle_status', methods=['POST'])
def account_toggle_status():
    return handle_route_action(account.toggle_status)
