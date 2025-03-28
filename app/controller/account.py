from app.sql_manager import SqlManager as db

class AccountOperationError(Exception):
    pass

def toggle_status(id_user, request_params):
    try:
        query = "update ACCOUNT set ACCOUNT_STATUS = (ACCOUNT_STATUS + 1) %2 where ID_ACCOUNT = (%s) and ID_USER = (%s)"
        db.execute_query(query, (request_params['id_account'], id_user), commit=True)
    except Exception as err:
        print(f"Could not open/close the account : {err}")
        raise

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
    nb_rows = len(result)
    return bool(nb_rows)

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
    nb_rows = len(result)
    print(f"The account {id_account} has {nb_rows} rows.")
    return not bool(nb_rows)

def fetch_all(id_user, unused):
    try:
        query = (
            "select acc.ID_ACCOUNT as id, ACCOUNT_NAME as name, ACCOUNT_TYPE as type, ACCOUNT_STATUS as status, "
            "ifnull(sum(txn.TRANSACTION_AMOUNT * txn.TRANSACTION_FLOW), 0) as balance, "
            "case when count(txn.ID_TRANSACTION) > 0 then 0 else 1 end as can_be_deleted "
            "from ACCOUNT acc "
            "left join TRANSACTION txn on txn.ID_ACCOUNT = acc.ID_ACCOUNT "
            "where acc.ID_USER = %s "
            "group by acc.ID_ACCOUNT"
        )
        result = db.execute_query(query, (id_user,), fetch=True, dictionary=True)
        return result
    except Exception as err:
        print(f"Could not fetch accounts : {err}")
        raise

def create(id_user, request_params):
    acc_name = request_params['account_name']
    acc_type = request_params['account_type']

    if acc_name is None:
        raise ValueError("Account name can't be empty.")
    acc_name = str(acc_name).strip()
    if acc_name == '':
        raise ValueError("Account name can't be empty.")
    if len(acc_name) > 50:
        raise ValueError("Account name can't be more than 50 characters.")
    if acc_type is None or int(acc_type) not in (1, 2):
        raise ValueError("Account type must be 1 or 2.")
    try:
        query = "insert into ACCOUNT (ID_USER, ACCOUNT_NAME, ACCOUNT_TYPE) values (%s, %s, %s)"
        db.execute_query(query, (id_user, acc_name, acc_type), commit=True)
    except Exception as error:
        print(f"Exception in account.create() : {type(error)} - {type(error).__name__} - {error}")
        raise error

def delete(id_user, request_params):
    id_account = request_params['id_account']
    try:
        if id_account is None or not str(id_account).strip():
            raise AccountOperationError(400, "ID account can't be empty.")
        id_account = int(id_account)
        if not is_valid(id_account):
            raise AccountOperationError(404, "This account doesn't exist.")
        if not is_valid(id_account, id_user):
            raise AccountOperationError(403, "This account doesn't belong to this user.")
        if not is_empty(id_account):
            raise AccountOperationError(409, "This account has transactions. Delete the transactions first.")
        query = "delete from ACCOUNT where ID_ACCOUNT = (%s) and ID_USER = (%s)"
        db.execute_query(query, (request_params['id_account'], id_user), commit=True)
    except Exception as error:
        print(f"Exception in account.delete() : {type(error)} - {type(error).__name__} - {error}")
        raise error
