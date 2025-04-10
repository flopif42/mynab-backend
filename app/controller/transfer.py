from app.sql_manager import SqlManager as db
from app.controller import transaction
import app.controller.account as account
from app.exceptions import InvalidParametersError, AccountNotFoundError, AccountPermissionError
from app.utils import validate_not_empty

def create(id_user, request):
    try:
        id_account_outflow = int(validate_not_empty(request, 'id_account_outflow'))
        id_account_inflow = int(validate_not_empty(request, 'id_account_inflow'))
        amount = int(validate_not_empty(request, 'amount'))
        transfer_date = transaction.mysql_format_date(validate_not_empty(request, 'date'))

        if not account.is_valid(id_account_outflow) or not account.is_valid(id_account_inflow):
            raise AccountNotFoundError
        if not account.is_valid(id_account_outflow, id_user) or not account.is_valid(id_account_inflow, id_user):
            raise AccountPermissionError
        if id_account_outflow == id_account_inflow:
            raise InvalidParametersError("The from and to accounts must be different.")
        if request.json.get('memo'):
            memo = validate_not_empty(request, 'memo')
        else:
            memo = None
        insert_values = {
            "amount": amount,
            "txn_date": transfer_date,
            "memo": memo,
            "is_transfer": 1,
            "id_payee": None,
            "id_category": None
        }

        # 1. create outflow transaction
        insert_values['id_account'] = id_account_outflow
        insert_values['flow'] = -1
        id_txn_outflow = transaction.sql_create(id_user, **insert_values)

        # 2. create inflow transaction
        insert_values['id_account'] = id_account_inflow
        insert_values['flow'] = 1
        id_txn_inflow = transaction.sql_create(id_user, **insert_values)

        # 3. create transfer record
        query = '''
                insert into TRANSFER 
                (ID_USER, ID_TRANSACTION_OUTFLOW, ID_TRANSACTION_INFLOW ) 
                values (%s, %s, %s)
                '''
        db.execute_query(query, (id_user, id_txn_outflow, id_txn_inflow), commit=True)
        return ''
    except ValueError:
        raise InvalidParametersError

# Utilities functions
def delete(id_user, id_transfer):
    # Retrieve the transcation ids associated with the transfer
    query_retrieve = "select ID_TRANSACTION_OUTFLOW, ID_TRANSACTION_INFLOW from TRANSFER where ID_TRANSFER = (%s)"
    result_retrieve = db.execute_query(query_retrieve, (id_transfer,), fetch=True)

    # delete the row in the TRANSFER table
    query = "delete from TRANSFER where ID_USER = (%s) and ID_TRANSFER = (%s)"
    db.execute_query(query, (id_user, id_transfer,), commit=True)

    # delete the associated rows in the TRANSACTION table
    query = "delete from TRANSACTION where ID_USER = (%s) and ID_TRANSACTION in ((%s), (%s))"
    db.execute_query(query, (id_user,) + result_retrieve[0], commit=True)
