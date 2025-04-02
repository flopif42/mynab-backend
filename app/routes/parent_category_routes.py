from flask import Blueprint, request
from flasgger import swag_from
from http import HTTPStatus
from app.routes.handler import handle_route_action
from app.controller import child_category, parent_category

parent_category_bp = Blueprint('parent_category', __name__)

# Parent categories routes
@parent_category_bp.route('/category/create_parent', methods=['POST'])
@swag_from('../docs/parent_category/parent_category_create.yml')
def parent_category_create():
    return handle_route_action(parent_category.create, mode='create')

@parent_category_bp.route('/category/delete_parent', methods=['DELETE'])
@swag_from('../docs/parent_category/parent_category_delete.yml')
def parent_category_delete():
    return handle_route_action(parent_category.delete, mode='delete')

@parent_category_bp.route('/category/move_parent', methods=['POST'])
def parent_category_move():
    return handle_route_action(parent_category.set_position)
