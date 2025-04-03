from app.sql_manager import SqlManager as db
from http import HTTPStatus
from app.exceptions import OperationError
from app.utils import validate_not_empty

def create(id_user, request):
    payee_name = validate_not_empty(request, 'payee_name')
    if len(payee_name) > 70:
        raise OperationError(HTTPStatus.BAD_REQUEST, "Payee name can't be more than 70 characters.")
    query = "insert into PAYEE (ID_USER, PAYEE_NAME) values (%s, %s)"
    db.execute_query(query, (id_user, payee_name), commit=True)

def delete(id_user, request):
    try:
        id_payee = int(validate_not_empty(request, 'id_payee'))
        if not is_valid(id_payee):
            raise OperationError(HTTPStatus.NOT_FOUND, "This payee doesn't exist.")
        if not is_valid(id_payee, id_user):
            raise OperationError(HTTPStatus.FORBIDDEN, "This payee doesn't belong to this user.")
        if not is_deletable(id_payee):
            raise OperationError(HTTPStatus.CONFLICT, "This payee has transactions. Delete the transactions first.")
        query = "delete from PAYEE where ID_PAYEE = (%s) and ID_USER = (%s)"
        db.execute_query(query, (id_payee, id_user), commit=True)
    except ValueError:
        raise OperationError(HTTPStatus.BAD_REQUEST, "Invalid ID payee.")

def list(id_user, request):
    query = '''
            select p.ID_PAYEE as id, p.PAYEE_NAME as name, 
            case when count(txn.ID_TRANSACTION) > 0 then 0 else 1 end as can_be_deleted 
            from PAYEE p left join TRANSACTION txn on txn.ID_PAYEE = p.ID_PAYEE 
            where p.ID_USER = %s 
            group by p.ID_PAYEE
            '''
    result = db.execute_query(query, (id_user,), fetch=True, dictionary=True)
    return result

def is_valid(id_payee, id_user=None):
    """
    This function is used to check the existence of id_payee in the table. If id_user is provided,
    it checks that this id_payee belongs to the right user.
    """
    query = 'select ID_PAYEE from PAYEE where ID_PAYEE = %s '
    values = (id_payee,)
    if id_user:
        query += 'and ID_USER = (%s)'
        values += (id_user,)
    result = db.execute_query(query, values, fetch=True)
    return bool(len(result))

def is_deletable(id_payee):
    """
    This function is used to check if the payee is free of transactions.
    """
    query = '''
            select ID_TRANSACTION as nb_txn
            from PAYEE p
            inner join TRANSACTION txn
              on txn.ID_PAYEE = p.ID_PAYEE
            where p.ID_PAYEE = %s
            '''
    result = db.execute_query(query, (id_payee, ), fetch=True)
    return not bool(len(result))
