from http import HTTPStatus
from flask import request
from app.sql_manager import SqlManager as db
from app.exceptions import OperationError
from app.utils import validate_not_empty

# Create a parent category
def create(id_user, request):
    parent_category_name = validate_not_empty(request, 'parent_category_name')
    if len(parent_category_name) > 50:
        raise OperationError(HTTPStatus.BAD_REQUEST, "Parent category name can't be more than 50 characters.")
    query = '''
            insert into PARENT_CATEGORY 
            select (%s) as ID_USER, max(ID_PARENT_CATEGORY)+1 as ID_PARENT_CATEGORY, (%s) as PARENT_CATEGORY_NAME, max(PARENT_CATEGORY_POSITION)+1 as position 
            from PARENT_CATEGORY where ID_USER = (%s)
            '''
    db.execute_query(query, (id_user, parent_category_name, id_user), commit=True)

def delete(id_user, request_params):
    try:
        id_parent = validate_not_empty(request, 'id_parent')
        id_parent = int(id_parent)
        if not is_valid(id_parent, id_user):
            raise OperationError(HTTPStatus.NOT_FOUND, "This parent category doesn't exist.")
        if not is_deletable(id_parent, id_user):
            raise OperationError(HTTPStatus.CONFLICT, "This parent category has subcategories.")
        if id_parent == 0:
            raise OperationError(HTTPStatus.BAD_REQUEST, "ID parent can't 0.")
        query = "delete from PARENT_CATEGORY where ID_PARENT_CATEGORY = (%s) and ID_USER = (%s)"
        db.execute_query(query, (id_parent, id_user), commit=True)
    except ValueError:
        raise OperationError(HTTPStatus.BAD_REQUEST, "Invalid ID parent.")

def is_valid(id_parent, id_user):
    """
    This function is used to check the existence of id_parent_category in the table for this user.
    """
    query = 'select ID_PARENT_CATEGORY from PARENT_CATEGORY where ID_PARENT_CATEGORY = %s and ID_USER = (%s)'
    result = db.execute_query(query, (id_parent, id_user), fetch=True)
    return bool(len(result))

def is_deletable(id_parent, id_user):
    """
    This function is used to check if the parent category is free of subcategories.
    """
    query = '''
            select ID_CATEGORY
            from PARENT_CATEGORY p_cat
            inner join CATEGORY cat
              on cat.ID_PARENT_CATEGORY = p_cat.ID_PARENT_CATEGORY
              and cat.ID_USER = p_cat.ID_USER 
            where p_cat.ID_PARENT_CATEGORY = %s and p_cat.ID_USER = %s
            '''
    result = db.execute_query(query, (id_parent, id_user), fetch=True)
    return not bool(len(result))
