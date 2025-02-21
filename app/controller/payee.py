import app.db as db

def validate_owner(id_user, id_payee):
    query = "select 1 from PAYEE where ID_USER = %s and ID_PAYEE = %s"
    rows = db.execute_query(query, (id_user, id_payee), fetch=True)
    return len(rows) > 0

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

def create(id_user, request_params):
    try:
        query = "INSERT INTO PAYEE (ID_USER, PAYEE_NAME) VALUES (%s, %s)"
        values = (id_user, request_params['payee_name'])
        db.execute_query(query, values, commit=True)
    except Exception as err:
        print(f"Could not create the oayee : {err}")
        raise

def delete(id_user, request_params):
    # 1. Make sure the id_payee belongs to the right user.
    if not validate_owner(id_user, request_params['id_payee']):
        print(f"Error : Payee with id {id_payee} does not belong to user with id {id_user}.")
        raise
    try:
        query = "delete from PAYEE where ID_PAYEE = (%s)"
        db.execute_query(query, (request_params['id_payee'],), commit=True)
    except Exception as err:
        print(f"Could not delete the payee : {err}")
        raise
