import json
from app.sql_manager import SqlManager as db

# Create a parent category
def create(id_user, request_params):
    try:
        query = (
            "insert into PARENT_CATEGORY "
            "select (%s) as ID_USER, max(ID_PARENT_CATEGORY)+1 as ID_PARENT_CATEGORY, (%s) as PARENT_CATEGORY_NAME, max(PARENT_CATEGORY_POSITION)+1 as position "
            "from PARENT_CATEGORY "
            "where ID_USER = (%s)"
        )
        db.execute_query(query, (id_user, request_params['parent_category_name'], id_user), commit=True)
    except Exception as err:
        print(f"Could not create the parent category : {err}")
        raise

def delete(id_user, request_params):
    try:
        query = "delete from PARENT_CATEGORY where ID_PARENT_CATEGORY = (%s) and ID_USER = (%s)"
        db.execute_query(query, (request_params['id_parent'], id_user), commit=True)
    except Exception as err:
        print(f"Could not delete the parent category : {err}")
        raise

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
