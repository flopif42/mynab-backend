import json
from app.sql_manager import SqlManager as db
from http import HTTPStatus

class CategoryOperationError(Exception):
    pass

# Create a parent category
def create(id_user, request_params):
    parent_category_name = request_params['parent_category_name']
    if parent_category_name is None:
        raise ValueError("Parent category name can't be empty.")
    parent_category_name = parent_category_name.strip()
    if parent_category_name == '':
        raise ValueError("Parent category name can't be empty.")
    if len(parent_category_name) > 50:
        raise ValueError("Parent category name can't be more than 50 characters.")
    try:
        query = '''
                insert into PARENT_CATEGORY 
                select (%s) as ID_USER, max(ID_PARENT_CATEGORY)+1 as ID_PARENT_CATEGORY, (%s) as PARENT_CATEGORY_NAME, max(PARENT_CATEGORY_POSITION)+1 as position 
                from PARENT_CATEGORY 
                where ID_USER = (%s)
                '''
        db.execute_query(query, (id_user, parent_category_name, id_user), commit=True)
    except Exception as error:
        print(f"Exception in parent_category.create() : {type(error)} - {type(error).__name__} - {error}")
        raise error

def delete(id_user, request_params):
    id_parent = request_params['id_parent']
    try:
        if id_parent is None or not str(id_parent).strip():
            raise CategoryOperationError(HTTPStatus.BAD_REQUEST, "ID parent can't be empty.")
        id_parent = int(id_parent)
        if not is_valid(id_parent, id_user):
            raise CategoryOperationError(HTTPStatus.NOT_FOUND, "This parent category doesn't exist.")
        if not is_deletable(id_parent, id_user):
            raise CategoryOperationError(HTTPStatus.CONFLICT, "This parent category has subcategories.")
        if id_parent == 0:
            raise CategoryOperationError(HTTPStatus.BAD_REQUEST, "ID parent can't 0.")
        query = "delete from PARENT_CATEGORY where ID_PARENT_CATEGORY = (%s) and ID_USER = (%s)"
        db.execute_query(query, (id_parent, id_user), commit=True)
    except Exception as error:
        print(f"Exception in parent_category.delete() : {type(error)} - {type(error).__name__} - {error}")
        raise error

def set_position(id_user, request_params):
    id_parent_category = request_params['id_parent_category']
    new_position = request_params['new_position']

    # "Income" cannot be moved and no parent category can be set to position 1
    if id_parent_category == 0 or new_position == 1:
        return

    parent_positions = db.execute_query("select ID_PARENT_CATEGORY, PARENT_CATEGORY_POSITION from PARENT_CATEGORY where ID_USER = (%s)", (id_user,), fetch=True)
    nb_parent_categories = len(parent_positions)
    sorted_list = sorted(parent_positions, key=lambda tup: tup[1])
    new_list = []
    for parent_category in sorted_list:
        if parent_category[0] == id_parent_category:
            saved = parent_category
        else:
            new_list.append(parent_category)
    new_list.insert(new_position-1, saved)
    for i in range(nb_parent_categories):
        db.execute_query("update PARENT_CATEGORY set PARENT_CATEGORY_POSITION=(%s) where ID_PARENT_CATEGORY=(%s)", (i+1, new_list[i][0]), commit=True)

def is_valid(id_parent, id_user):
    """
    This function is used to check the existence of id_parent_category in the table for this user.
    """
    query = 'select ID_PAYEE from PAYEE where ID_PAYEE = %s and ID_USER = (%s)'
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
