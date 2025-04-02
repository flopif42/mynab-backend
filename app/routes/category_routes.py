from flask import Blueprint, request
from flasgger import swag_from
from http import HTTPStatus
from app.routes.handler import handle_route_action
from app.controller import child_category, parent_category

category_bp = Blueprint('category', __name__)

@category_bp.route('/category/list', methods=['GET'])
def category_list():
    return handle_route_action(child_category.fetch_all)

@category_bp.route('/category/create', methods=['POST'])
def category_create():
    return handle_route_action(child_category.create, create=True)

@category_bp.route('/category/delete', methods=['POST'])
def category_delete():
    return handle_route_action(child_category.delete)
