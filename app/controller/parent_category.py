import json
import app.db as db

def validate_owner(id_user, id_parent_category):
    query = "select 1 from PARENT_CATEGORY where ID_USER = %s and ID_PARENT_CATEGORY = %s"
    rows = db.execute_query(query, (id_user, id_parent_category), fetch=True)
    return len(rows) > 0

# Create a parent category
def create(id_user, request_params):
    try:
        query = (
            "insert into PARENT_CATEGORY "
            "select (%s) as ID_PARENT_CATEGORY, (%s) as ID_USER, (%s) as PARENT_CATEGORY_NAME, ifnull(max(PARENT_CATEGORY_POSITION), 0) + 1 as position "
            "from PARENT_CATEGORY"
        )
        db.execute_query(query, (db.get_next_val('CATEGORIES'), id_user, request_params['parent_category_name']), commit=True)
    except Exception as err:
        print(f"Could not create the parent category : {err}")
        raise

def delete(id_user, request_params):
    # 1. Make sure the id_parent belongs to the right user.
    if not validate_owner(id_user, request_params['id_parent']):
        print(f"Error : Parent with id {request_params['id_parent']} does not belong to user with id {id_user}.")
        raise
    try:
        query = "delete from PARENT_CATEGORY where ID_PARENT_CATEGORY = (%s)"
        db.execute_query(query, (request_params['id_parent'],), commit=True)
    except Exception as err:
        print(f"Could not delete the parent category : {err}")
        raise

def set_position(id_user, request_params):
    id_parent_category = request_params['id_parent_category']
    new_position = request_params['new_position']
    # Make sure the id_parent_category belongs to the right user.
    if not validate_owner(id_user, id_parent_category):
        print(f"Error : Parent with id {id_parent_category} does not belong to user with id {id_user}.")
        raise
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
        db.execute_query("update PARENT_CATEGORY set PARENT_CATEGORY_POSITION=(%s) where ID_PARENT_CATEGORY=(%s)", (nb_parent_categories+i+1, new_list[i][0]), commit=True)
    for i in range(nb_parent_categories):
        db.execute_query("update PARENT_CATEGORY set PARENT_CATEGORY_POSITION=(%s) where ID_PARENT_CATEGORY=(%s)", (i+1, new_list[i][0]), commit=True)
