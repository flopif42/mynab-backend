from app.db import DbPool, execute_query

def validate_owner(id_user, id_account):
    query = "select 1 from ACCOUNT where ID_USER = %s and ID_ACCOUNT = %s"
    rows = execute_query(query, (id_user, id_account), fetch=True)
    return len(rows) > 0

def fetch_all(id_user, unused):
    try:
        query = (
            "select acc.ID_ACCOUNT as id, ACCOUNT_NAME as name, ACCOUNT_TYPE as type, ACCOUNT_STATUS as status, "
            "ifnull(truncate(sum(txn.TRANSACTION_AMOUNT * txn.TRANSACTION_FLOW)/100, 2), 0) as balance, "
            "case when count(txn.ID_TRANSACTION) > 0 then 0 else 1 end as can_be_deleted "
            "from ACCOUNT acc "
            "left join TRANSACTION txn on txn.ID_ACCOUNT = acc.ID_ACCOUNT "
            "where acc.ID_USER = %s "
            "group by acc.ID_ACCOUNT"
        )
        result = execute_query(query, (str(id_user),), fetch=True, dictionary=True)
        return result
    except Exception as err:
        print(f"Could not fetch accounts : {err}")
        raise

def create(id_user, request_params):
    try:
        query = "INSERT INTO ACCOUNT (ID_USER, ACCOUNT_NAME, ACCOUNT_TYPE) VALUES (%s, %s, %s)"
        execute_query(query, (id_user, request_params['account_name'], request_params['account_type']), commit=True)
    except Exception as err:
        print(f"Could not create the account : {err}")
        raise

def delete(id_user, request_params):
    # 1. Make sure the id_account belongs to the right user.
    if not validate_owner(id_user, request_params['id_account']):
        print(f"Error : Account with id {request_params['id_account']} does not belong to user with id {id_user}.")
        raise
    try:
        query = "delete from ACCOUNT where ID_ACCOUNT = (%s)"
        execute_query(query, (request_params['id_account'],), commit=True)
    except Exception as err:
        print(f"Could not delete the account : {err}")
        raise

def toggle_status(id_user, request_params):
    # 1. Make sure the id_account belongs to the right user.
    if not validate_owner(id_user, request_params['id_account']):
        print(f"Error : Account with id {request_params['id_account']} does not belong to user with id {id_user}.")
        raise
    try:
        query = "update ACCOUNT set ACCOUNT_STATUS = (ACCOUNT_STATUS + 1) %2 where ID_ACCOUNT = (%s)"
        execute_query(query, (request_params['id_account'],), commit=True)
    except Exception as err:
        print(f"Could not open/close the account : {err}")
        raise
