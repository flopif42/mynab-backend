from http import HTTPStatus
from app.sql_manager import SqlManager
import app.controller.parent_category as pc
from app.exceptions import OperationError
from app.utils import validate_not_empty

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
        parent_categories = SqlManager.execute_query(query, (id_user,), fetch=True, dictionary=True)
        for parent_category in parent_categories:
            query = """
                    select cat.ID_CATEGORY as id, CATEGORY_NAME as name, ID_PARENT_CATEGORY as id_parent, 
                        case when count(ID_TRANSACTION) > 0 then 0 else 1 end as can_be_deleted 
                    from CATEGORY cat left join TRANSACTION txn on txn.ID_USER = cat.ID_USER and txn.ID_CATEGORY = cat.ID_CATEGORY 
                    where cat.ID_USER = (%s) and ID_PARENT_CATEGORY = (%s) 
                    group by cat.ID_CATEGORY , CATEGORY_NAME , ID_PARENT_CATEGORY 
                    """
            categories = SqlManager.execute_query(query, (id_user, parent_category['id']), fetch=True, dictionary=True)
            parent_category['child_categories'] = []
            for category in categories:
                parent_category['child_categories'].append(category)
        return parent_categories
    except Exception as err:
        print(f"Could not fetch categories : {err}")
        raise

# Create a category and attach it to an existing parent category
def create(id_user, request):
    id_parent = validate_not_empty(request, 'id_parent')
    id_parent = int(id_parent)
    if not pc.is_valid(id_parent, id_user):
        raise OperationError(HTTPStatus.NOT_FOUND, "This parent category doesn't exist.")
    if id_parent == 0:
        raise OperationError(HTTPStatus.BAD_REQUEST, "ID parent can't 0.")
    category_name = validate_not_empty(request, 'category_name')
    if len(category_name) > 50:
        raise OperationError(HTTPStatus.BAD_REQUEST, "Category name can't be more than 50 characters.")
    try:
        query = '''
                insert into CATEGORY 
                select (%s) as ID_USER, max(ID_CATEGORY)+1 as ID_CATEGORY, (%s) as ID_PARENT_CATEGORY, (%s) as CATEGORY_NAME 
                from CATEGORY 
                where ID_USER = (%s) 
                '''
        SqlManager.execute_query(query, (id_user, id_parent, category_name, id_user), commit=True)
    except ValueError:
        raise OperationError(HTTPStatus.BAD_REQUEST, "Invalid ID parent.")

def delete(id_user, request_params):
    try:
        query = "delete from BUDGET_LINE where ID_USER = (%s) and ID_CATEGORY = (%s) and ID_CATEGORY <> 0"
        SqlManager.execute_query(query, (id_user, request_params['id_category'],), commit=True)
        query = "delete from CATEGORY where ID_USER = (%s) and ID_CATEGORY = (%s) and ID_CATEGORY <> 0"
        SqlManager.execute_query(query, (id_user, request_params['id_category'],), commit=True)
    except Exception as err:
        print(f"Could not delete the category : {err}")
        raise
