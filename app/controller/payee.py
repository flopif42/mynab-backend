from app.sql_manager import SqlManager as db

class PayeeOperationError(Exception):
    pass

def create(id_user, request_params):
    payee_name = request_params['payee_name']
    if payee_name is None:
        raise ValueError("Payee name can't be empty.")
    payee_name = payee_name.strip()
    if payee_name == '':
        raise ValueError("Payee name can't be empty.")
    if len(payee_name) > 70:
        raise ValueError("Payee name can't be more than 70 characters.")
    try:
        query = "insert into PAYEE (ID_USER, PAYEE_NAME) values (%s, %s)"
        db.execute_query(query, (id_user, payee_name), commit=True)
    except Exception as error:
        print(f"Exception in payee.create() : {type(error)} - {type(error).__name__} - {error}")
        raise error

def delete(id_user, request_params):
    id_payee = request_params['id_payee']
    try:
        if id_payee is None or not str(id_payee).strip():
            raise PayeeOperationError(400, "ID payee can't be empty.")
        id_payee = int(id_payee)
        if not is_valid(id_payee):
            raise PayeeOperationError(404, "This payee doesn't exist.")
        if not is_valid(id_payee, id_user):
            raise PayeeOperationError(403, "This payee doesn't belong to this user.")
        if not is_deletable(id_payee):
            raise PayeeOperationError(409, "This payee has transactions. Delete the transactions first.")
        query = "delete from PAYEE where ID_PAYEE = (%s) and ID_USER = (%s)"
        db.execute_query(query, (id_payee, id_user), commit=True)
    except Exception as error:
        print(f"Exception in payee.delete() : {type(error)} - {type(error).__name__} - {error}")
        raise error

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
