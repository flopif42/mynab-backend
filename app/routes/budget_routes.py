from flask import Blueprint
from app import handle_route_action
from app.controller import budget

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget/list', methods=['GET'])
def budget_list():
    return handle_route_action(budget.fetch)

@budget_bp.route('/budget/set_funded', methods=['POST'])
def budget_set_funded():
    return handle_route_action(budget.set_funded)
