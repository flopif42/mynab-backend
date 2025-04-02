from flask import Blueprint, request
from flasgger import swag_from
from http import HTTPStatus
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
@swag_from('../docs/parent_category/parent_category_create.yml')
def parent_category_create():
    try:
        if not request.is_json or 'parent_category_name' not in request.json:
            raise ValueError
        return handle_route_action(parent_category.create, create=True)
    except ValueError:
        return "", HTTPStatus.BAD_REQUEST
    except Exception as error:
        print(f"Exception in payee_routes.payee_create() : {type(error)} - {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@category_bp.route('/category/delete_parent', methods=['DELETE'])
@swag_from('../docs/parent_category/parent_category_delete.yml')
def parent_category_delete():
    try:
        if not request.is_json or 'id_parent' not in request.json:
            raise CategoryOperationError(HTTPStatus.BAD_REQUEST, "The parameter ID parent is required.")
        return handle_route_action(parent_category.delete, delete=True)
    except ValueError:
        return "", HTTPStatus.BAD_REQUEST
    except CategoryOperationError as error:
        return { "error": error.args[1] }, error.args[0]
    except Exception as error:
        print(f"Exception in payee_routes.payee_delete() : {type(error).__name__} - {error}")
        return "", HTTPStatus.INTERNAL_SERVER_ERROR

@category_bp.route('/category/move_parent', methods=['POST'])
def parent_category_move():
    return handle_route_action(parent_category.set_position)
