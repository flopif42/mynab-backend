from http import HTTPStatus
from app.sql_manager import SqlManager as db
from app.exceptions import OperationError
from app.utils import validate_not_empty

def list(id_user, request):
    query = '''
            select acc.ID_ACCOUNT as id, ACCOUNT_NAME as name, ACCOUNT_TYPE as type, ACCOUNT_STATUS as status, 
            ifnull(sum(txn.TRANSACTION_AMOUNT * txn.TRANSACTION_FLOW), 0) as balance, 
            case when count(txn.ID_TRANSACTION) > 0 then 0 else 1 end as can_be_deleted 
            from ACCOUNT acc 
            left join TRANSACTION txn on txn.ID_ACCOUNT = acc.ID_ACCOUNT 
            where acc.ID_USER = %s 
            group by acc.ID_ACCOUNT
            '''
    return db.execute_query(query, (id_user,), fetch=True, dictionary=True)

def create(id_user, request):
    try:    
        account_name = validate_not_empty(request, 'account_name')
        account_type = int(validate_not_empty(request, 'account_type'))
        if len(account_name) > 50:
            raise OperationError(HTTPStatus.BAD_REQUEST, "Account name can't be more than 50 characters.")
        if account_type not in (1, 2):
            raise OperationError(HTTPStatus.BAD_REQUEST, "Account type must be 1 or 2.")
        query = "insert into ACCOUNT (ID_USER, ACCOUNT_NAME, ACCOUNT_TYPE) values (%s, %s, %s)"
        db.execute_query(query, (id_user, account_name, account_type), commit=True)
    except ValueError:
        raise OperationError(HTTPStatus.BAD_REQUEST, "Invalid account type value.")

def delete(id_user, request):
    try:
        id_account = int(validate_not_empty(request, 'id_account'))
        if not is_valid(id_account):
            raise AccountNotExistError
        if not is_valid(id_account, id_user):
            raise AccountWrongOwnerError
        if not is_empty(id_account):
            raise AccountNotEmptyError
        query = "delete from ACCOUNT where ID_ACCOUNT = (%s) and ID_USER = (%s)"
        db.execute_query(query, (id_account, id_user), commit=True)
    except ValueError:
        raise OperationError(HTTPStatus.BAD_REQUEST, "Invalid ID account.")

def set_status(id_user, request):
    """
    This function is used to set the status to an account to the new value. 1 = open, 0 = closed
    """
    try:
        id_account = int(validate_not_empty(request, 'id_account'))
        account_status = int(validate_not_empty(request, 'account_status'))
        if not is_valid(id_account):
            raise OperationError(HTTPStatus.NOT_FOUND, "This account doesn't exist.")
        if not is_valid(id_account, id_user):
            raise OperationError(HTTPStatus.FORBIDDEN, "This account doesn't belong to this user.")
        if account_status not in (0, 1):
            raise OperationError(HTTPStatus.BAD_REQUEST, "Invalid account status value.")
        query = "update ACCOUNT set ACCOUNT_STATUS = (%s) where ID_ACCOUNT = (%s) and ID_USER = (%s)"
        db.execute_query(query, (account_status, id_account, id_user), commit=True)
    except ValueError:
        raise OperationError(HTTPStatus.BAD_REQUEST, "Invalid parameters.")

# Helper functions
def is_valid(id_account, id_user=None):
    """
    This function is used to check the existence of id_account in the table. If id_user is provided,
    it checks that this id_account belongs to the right user.
    """
    query = 'select ID_ACCOUNT from ACCOUNT where ID_ACCOUNT = %s '
    values = (id_account, )
    if id_user:
        query += 'and ID_USER = (%s)'
        values += (id_user,)
    result = db.execute_query(query, values, fetch=True)
    return bool(len(result))

def is_empty(id_account):
    """
    This function is used to check if the account is free of transactions.
    """
    query = '''
            select ID_TRANSACTION as nb_txn
            from ACCOUNT acc
            inner join TRANSACTION txn
              on txn.ID_ACCOUNT = acc.ID_ACCOUNT
            where acc.ID_ACCOUNT = %s
            '''
    result = db.execute_query(query, (id_account, ), fetch=True)
    return not bool(len(result))
