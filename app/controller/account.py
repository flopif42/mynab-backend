import app.db as db

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
    try:
        query = "INSERT INTO ACCOUNT (ID_USER, ACCOUNT_NAME, ACCOUNT_TYPE) VALUES (%s, %s, %s)"
        db.execute_query(query, (id_user, request_params['account_name'], request_params['account_type']), commit=True)
    except Exception as err:
        print(f"Could not create the account : {err}")
        raise

def delete(id_user, request_params):
    try:
        query = "delete from ACCOUNT where ID_ACCOUNT = (%s) and ID_USER = (%s)"
        db.execute_query(query, (request_params['id_account'], id_user), commit=True)
    except Exception as err:
        print(f"Could not delete the account : {err}")
        raise

def toggle_status(id_user, request_params):
    try:
        query = "update ACCOUNT set ACCOUNT_STATUS = (ACCOUNT_STATUS + 1) %2 where ID_ACCOUNT = (%s) and ID_USER = (%s)"
        db.execute_query(query, (request_params['id_account'], id_user), commit=True)
    except Exception as err:
        print(f"Could not open/close the account : {err}")
        raise
