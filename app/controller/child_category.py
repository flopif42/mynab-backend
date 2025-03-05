import json
import app.db as db
import app.controller.parent_category as p_cat

def fetch_all(id_user, unused):
    try:
        query = """
                select par.ID_PARENT_CATEGORY as id, PARENT_CATEGORY_NAME as name, PARENT_CATEGORY_POSITION as position, 
                    case when count(chi.ID_CATEGORY) > 0 then 0 else 1 end as can_be_deleted
                from PARENT_CATEGORY par
                left join CATEGORY chi
                    on chi.ID_PARENT_CATEGORY = par.ID_PARENT_CATEGORY and chi.ID_USER = par.ID_USER
                where par.ID_USER = (%s) and par.ID_PARENT_CATEGORY > 0
                group by par.ID_PARENT_CATEGORY, PARENT_CATEGORY_NAME, PARENT_CATEGORY_POSITION

                """
        parent_categories = db.execute_query(query, (id_user,), fetch=True, dictionary=True)
        for parent_category in parent_categories:
            query = """
                    select cat.ID_CATEGORY as id, CATEGORY_NAME as name, ID_PARENT_CATEGORY as id_parent, 
                        case when count(ID_TRANSACTION) > 0 then 0 else 1 end as can_be_deleted 
                    from CATEGORY cat left join TRANSACTION txn on txn.ID_USER = cat.ID_USER and txn.ID_CATEGORY = cat.ID_CATEGORY 
                    where cat.ID_USER = (%s) and ID_PARENT_CATEGORY = (%s) 
                    group by cat.ID_CATEGORY , CATEGORY_NAME , ID_PARENT_CATEGORY 
                    """
            categories = db.execute_query(query, (id_user, parent_category['id']), fetch=True, dictionary=True)
            parent_category['child_categories'] = []
            for category in categories:
                parent_category['child_categories'].append(category)
        return parent_categories
    except Exception as err:
        print(f"Could not fetch categories : {err}")
        raise

# Create a category and attach it to an existing parent category
def create(id_user, request_params):
    try:
        query = (
            "insert into CATEGORY "
            "select (%s) as ID_USER, max(ID_CATEGORY)+1 as ID_CATEGORY, (%s) as ID_PARENT_CATEGORY, (%s) as CATEGORY_NAME "
            "from CATEGORY "
            "where ID_USER = (%s) "
        )
        db.execute_query(query, (id_user, request_params['id_parent'], request_params['category_name'], id_user), commit=True)
    except Exception as err:
        print(f"Could not create the category : {err}")
        raise

def delete(id_user, request_params):
    try:
        query = "delete from BUDGET_LINE where ID_USER = (%s) and ID_CATEGORY = (%s) and ID_CATEGORY <> 0"
        db.execute_query(query, (id_user, request_params['id_category'],), commit=True)
        query = "delete from CATEGORY where ID_USER = (%s) and ID_CATEGORY = (%s) and ID_CATEGORY <> 0"
        db.execute_query(query, (id_user, request_params['id_category'],), commit=True)
    except Exception as err:
        print(f"Could not delete the category : {err}")
        raise
