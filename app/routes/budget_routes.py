from flask import Blueprint
from app.routes import handle_route_action
from app.controller import budget

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget/list', methods=['GET'])
def budge_list():
    return handle_route_action(budget.fetch)
