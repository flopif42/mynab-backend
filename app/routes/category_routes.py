from flask import Blueprint
from app.routes import handle_route_action
from app.controller import category

category_bp = Blueprint('category', __name__)

@category_bp.route('/category/list', methods=['GET'])
def category_list():
    return handle_route_action(category.fetch_all)

@category_bp.route('/category/create', methods=['POST'])
def category_create():
    return handle_route_action(category.create)

@category_bp.route('/category/create_parent', methods=['POST'])
def parent_category_create():
    return handle_route_action(category.create_parent)

@category_bp.route('/category/delete', methods=['POST'])
def category_delete():
    return handle_route_action(category.delete)

@category_bp.route('/category/delete_parent', methods=['POST'])
def parent_category_delete():
    return handle_route_action(category.delete_parent)

@category_bp.route('/category/move_parent', methods=['POST'])
def parent_category_move():
    return handle_route_action(category.set_parent_position)
