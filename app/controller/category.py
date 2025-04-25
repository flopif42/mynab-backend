from app.sql_manager import SqlManager as db
from app.exceptions import InvalidParametersError, ParentCategoryNotFoundError, CategoryNotFoundError, CategoryNotEmptyError
from app.utils import validate_not_empty
import app.controller.parent_category as parent_category

def list(id_user, request):
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

# Create a category and attach it to an existing parent category
def create(id_user, request):
    try:
        id_parent = validate_not_empty(request, 'id_parent')
        id_parent = int(id_parent)
        if not parent_category.is_valid(id_parent, id_user):
            raise ParentCategoryNotFoundError
        if id_parent == 0:
            raise InvalidParametersError("ID parent can't 0.")
        category_name = validate_not_empty(request, 'category_name')
        if len(category_name) > 50:
            raise InvalidParametersError("Category name can't be more than 50 characters.")
        query = '''
                insert into CATEGORY 
                select (%s) as ID_USER, max(ID_CATEGORY)+1 as ID_CATEGORY, (%s) as ID_PARENT_CATEGORY, (%s) as CATEGORY_NAME 
                from CATEGORY where ID_USER = (%s) 
                '''
        db.execute_query(query, (id_user, id_parent, category_name, id_user), commit=True)
    except ValueError:
        raise InvalidParametersError("Invalid ID parent.")

def delete(id_user, request):
    try:
        id_category = validate_not_empty(request, 'id_category')
        id_category = int(id_category)
        if not is_valid(id_category, id_user):
            raise CategoryNotFoundError
        if not is_deletable(id_category, id_user):
            raise CategoryNotEmptyError
        if id_category == 0:
            raise InvalidParametersError("ID category can't 0.")
        query = "delete from BUDGET_LINE where ID_USER = (%s) and ID_CATEGORY = (%s) and ID_CATEGORY <> 0"
        db.execute_query(query, (id_user, id_category), commit=True)
        query = "delete from CATEGORY where ID_USER = (%s) and ID_CATEGORY = (%s) and ID_CATEGORY <> 0"
        db.execute_query(query, (id_user, id_category), commit=True)
    except ValueError:
        raise InvalidParametersError("Invalid ID category.")

def is_valid(id_category, id_user):
    """
    This function is used to check the existence of id_category in the table for this user.
    """
    query = 'select ID_CATEGORY from CATEGORY where ID_CATEGORY = %s and ID_USER = (%s)'
    result = db.execute_query(query, (id_category, id_user), fetch=True)
    return bool(len(result))

def is_deletable(id_category, id_user):
    """
    This function is used to check if the category is free of transactions.
    """
    query = '''
            select ID_TRANSACTION as nb_txn
            from CATEGORY cat
            inner join TRANSACTION txn
              on txn.ID_CATEGORY = cat.ID_CATEGORY
              and txn.ID_USER = cat.ID_USER
            where cat.ID_CATEGORY = %s and cat.ID_USER = %s
            '''
    result = db.execute_query(query, (id_category, id_user), fetch=True)
    return not bool(len(result)) # True if no rows are returned from the query, otherwise False
