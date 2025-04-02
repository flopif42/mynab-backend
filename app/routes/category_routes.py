from flask import Blueprint
from app.routes.handler import handle_route_action
from app.controller import child_category, parent_category

category_bp = Blueprint('category', __name__)

# Child categories routes
@category_bp.route('/category/list', methods=['GET'])
def category_list():
    return handle_route_action(child_category.fetch_all)

@category_bp.route('/category/create', methods=['POST'])
def category_create():
    return handle_route_action(child_category.create, create=True)

@category_bp.route('/category/delete', methods=['POST'])
def category_delete():
    return handle_route_action(child_category.delete)

# Parent categories routes
@category_bp.route('/category/create_parent', methods=['POST'])
def parent_category_create():
    return handle_route_action(parent_category.create, create=True)

@category_bp.route('/category/delete_parent', methods=['POST'])
def parent_category_delete():
    return handle_route_action(parent_category.delete, delete=True)

@category_bp.route('/category/move_parent', methods=['POST'])
def parent_category_move():
    return handle_route_action(parent_category.set_position)
