from app.sql_manager import SqlManager as db

def create(id_user, request_params):
    payee_name = request_params['payee_name']
    if payee_name is None:
        raise ValueError("Payee name can't be empty.")
    payee_name = payee_name.strip()
    if payee_name == '':
        raise ValueError("Payee name can't be empty.")
    if len(acc_name) > 70:
        raise ValueError("Payee name can't be more than 70 characters.")
    try:
        query = "insert into PAYEE (ID_USER, PAYEE_NAME) values (%s, %s)"
        db.execute_query(query, (id_user, request_params['payee_name']), commit=True)
    except Exception as error:
        print(f"Exception in payee.create() : {type(error)} - {type(error).__name__} - {error}")
        raise error

def delete(id_user, request_params):
    try:
        query = "delete from PAYEE where ID_PAYEE = (%s) and ID_USER = (%s)"
        db.execute_query(query, (request_params['id_payee'], id_user), commit=True)
    except Exception as err:
        print(f"Could not delete the payee : {err}")
        raise

def fetch_all(id_user, unused):
    try:
        query = (
            "select p.ID_PAYEE as id, p.PAYEE_NAME as name, "
            "case when count(txn.ID_TRANSACTION) > 0 then 0 else 1 end as can_be_deleted "
            "from PAYEE p left join TRANSACTION txn on txn.ID_PAYEE = p.ID_PAYEE "
            "where p.ID_USER = %s "
            "group by p.ID_PAYEE"
        )
        result = db.execute_query(query, (str(id_user),), fetch=True, dictionary=True)
        return result
    except Exception as err:
        print(f"Could not fetch payees : {err}")
        raise
