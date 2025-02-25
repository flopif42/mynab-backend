import app.db as db
from app.controller import account, transaction

#def validate_owner(id_user, id_transfer):
#    query = "select 1 from TRANSFER where ID_USER = %s and ID_TRANSFER = %s"
#    rows = db.execute_query(query, (id_user, id_transfer), fetch=True)
#    return len(rows) > 0

def create(id_user, request_params):
    # request_params contains the following :
    # id_account_outflow, id_account_inflow, amount, date, memo
    
    # Make sure the id_accounts belong to the right user.
    id_account_outflow = request_params['id_account_outflow']
    if not account.validate_owner(id_user, id_account_outflow):
        print(f"Error : Account with id {id_account_outflow} does not belong to user with id {id_user}.")
        raise
    id_account_inflow = request_params['id_account_inflow']
    if not account.validate_owner(id_user, id_account_inflow):
        print(f"Error : Account with id {id_account_inflow} does not belong to user with id {id_user}.")
        raise

    # Make sure the id_accounts From and To are different
    if id_account_outflow == id_account_inflow:
        print(f"Error : Cannot make transfer between the same account.")
        raise
    try:
        insert_values = {
            "amount": request_params['amount'],
            "date": request_params['date'],
            "memo": request_params['memo'],
            "is_transfer": 1
        }

        # 1. create outflow transaction
        insert_values['id_account'] = id_account_outflow
        insert_values['flow'] = -1
        id_txn_outflow = transaction.create(id_user, insert_values)

        # 2. create inflow transaction
        insert_values['id_account'] = id_account_inflow
        insert_values['flow'] = 1
        id_txn_inflow = transaction.create(id_user, insert_values)

        # 3. create transfer record
        query = (
            "insert into TRANSFER "
            "(ID_USER, ID_TRANSACTION_OUTFLOW, ID_TRANSACTION_INFLOW ) "
            "values (%s, %s, %s)"
        )
        result = db.execute_query(query, (id_user, id_txn_outflow, id_txn_inflow), commit=True)
        return result
    except Exception as err:
        print(f"Could not create transfer : {err}")
        return None

def delete(id_user, id_transfer):
    try:
        # Retrieve the transcation ids associated with the transfer
        query_retrieve = "select ID_TRANSACTION_OUTFLOW, ID_TRANSACTION_INFLOW from TRANSFER where ID_TRANSFER = (%s)"
        result_retrieve = db.execute_query(query_retrieve, (id_transfer,), fetch=True)

        # delete the transfer
        query = "delete from TRANSFER where ID_USER = (%s) and ID_TRANSFER = (%s)"
        result = db.execute_query(query, (id_user, id_transfer,), commit=True)

        # delete the associated transactions
        query = "delete from TRANSACTION where ID_USER = (%s) and ID_TRANSACTION in ((%s), (%s))"
        result = db.execute_query(query, (id_user,) + result_retrieve[0], commit=True)
        return result
    except Exception as err:
        print(f"Could not delete transfer: {err}")
        raise
