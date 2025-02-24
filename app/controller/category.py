import json
import app.db as db

def validate_owner(id_user, id_category):
    query = "select 1 from CATEGORY where ID_USER = %s and ID_CATEGORY = %s"
    rows = db.execute_query(query, (id_user, id_category), fetch=True)
    return len(rows) > 0

def validate_parent_owner(id_user, id_parent_category):
    query = "select 1 from PARENT_CATEGORY where ID_USER = %s and ID_PARENT_CATEGORY = %s"
    rows = db.execute_query(query, (id_user, id_parent_category), fetch=True)
    return len(rows) > 0

def fetch_all(id_user, unused):
    try:
        query = (
            "select ID_PARENT_CATEGORY as id, PARENT_CATEGORY_NAME as name, PARENT_CATEGORY_POSITION as position "
            "from PARENT_CATEGORY where ID_USER = (%s)"
        )
        parent_categories = db.execute_query(query, (str(id_user),), fetch=True, dictionary=True)
        for parent_category in parent_categories:
            query_children = (
                "select cat.ID_CATEGORY as id, CATEGORY_NAME as name, ID_PARENT_CATEGORY as id_parent, "
                "case when count(ID_TRANSACTION) > 0 then 0 else 1 end as can_be_deleted "
                "from CATEGORY cat left join TRANSACTION txn on txn.ID_CATEGORY = cat.ID_CATEGORY "
                "where cat.ID_USER = (%s) and ID_PARENT_CATEGORY = (%s) "
                "group by cat.ID_CATEGORY , CATEGORY_NAME , ID_PARENT_CATEGORY "
            )
            categories = db.execute_query(query_children, (id_user, parent_category['id']), fetch=True, dictionary=True)
            parent_category['child_categories'] = []
            for category in categories:
                parent_category['child_categories'].append(category)
        return parent_categories
    except Exception as err:
        print(f"Could not fetch categories : {err}")
        raise

# Create a parent category
def create_parent(id_user, request_params):
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

# Create a category and attach it to an existing parent category
def create(id_user, request_params):
    # 1. Make sure the id_parent belongs to the right user.
    if not validate_parent_owner(id_user, request_params['id_parent']):
        print(f"Error : Parent category with id {request_params['id_parent']} does not belong to user with id {id_user}.")
        raise
    try:
        query = "insert into CATEGORY (ID_CATEGORY, ID_USER, ID_PARENT_CATEGORY, CATEGORY_NAME) values (%s, %s, %s, %s)"
        db.execute_query(query, (db.get_next_val('CATEGORIES'), id_user, request_params['id_parent'], request_params['category_name']), commit=True)
    except Exception as err:
        print(f"Could not create the category : {err}")
        raise

def delete_parent(id_user, request_params):
    # 1. Make sure the id_parent belongs to the right user.
    if not validate_parent_owner(id_user, request_params['id_parent']):
        print(f"Error : Parent with id {request_params['id_parent']} does not belong to user with id {id_user}.")
        raise
    try:
        query = "delete from PARENT_CATEGORY where ID_PARENT_CATEGORY = (%s)"
        db.execute_query(query, (request_params['id_parent'],), commit=True)
    except Exception as err:
        print(f"Could not delete the parent category : {err}")
        raise

def delete(id_user, request_params):
    # 1. Make sure the id_category belongs to the right user.
    if not validate_owner(id_user, request_params['id_category']):
        print(f"Error : Category with id {request_params['id_category']} does not belong to user with id {id_user}.")
        raise
    try:
        query = "delete from CATEGORY where ID_CATEGORY = (%s)"
        db.execute_query(query, (request_params['id_category'],), commit=True)
    except Exception as err:
        print(f"Could not delete the category : {err}")
        raise

def set_parent_position(id_user, request_params):
    # Make sure the id_parent_category belongs to the right user.
    if not validate_parent_owner(id_user, request_params['id_parent_category']):
        print(f"Error : Parent with id {request_params['id_parent_category']} does not belong to user with id {id_user}.")
        raise

    query = "select ID_PARENT_CATEGORY, PARENT_CATEGORY_POSITION from PARENT_CATEGORY where ID_USER = (%s) order by ID_PARENT_CATEGORY"
    parent_positions = db.execute_query(query, (id_user,), fetch=True)
    new_position = request_params['new_position']

    print(parent_positions)

    my_list = sorted(parent_postitions, key=lambda tup: tup[1])
    print(my_list)
