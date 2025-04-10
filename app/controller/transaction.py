from mysql.connector.errors import IntegrityError
import datetime as dt
from app.sql_manager import SqlManager as db
from app.controller import account
from app.controller import transfer
from app.exceptions import InvalidParametersError, AccountNotFoundError
from app.utils import validate_not_empty

def list(id_user, request):
    try:
        query = """
                select a.ACCOUNT_NAME as account, 
                    txn.ID_TRANSACTION as id, 
                    case 
                        when (txn.IS_TRANSFER=1 and txn.TRANSACTION_FLOW = -1) then concat('Transfer to: ', acc_trs_out.ACCOUNT_NAME) 
                        when (txn.IS_TRANSFER=1 and txn.TRANSACTION_FLOW = 1) then concat('Transfer from: ', acc_trs_in.ACCOUNT_NAME) 
                    else PAYEE_NAME end as payee, 
                    CATEGORY_NAME as category, 
                    if(txn.TRANSACTION_FLOW=-1, 'Outflow', 'Inflow') as flow, 
                    txn.TRANSACTION_AMOUNT as amount, 
                    date_format(txn.TRANSACTION_DATE, '%d/%m/%Y') as date, 
                    txn.TRANSACTION_MEMO as memo 
                from TRANSACTION txn 
                    inner join ACCOUNT a on a.ID_ACCOUNT = txn.ID_ACCOUNT 
                    left join PAYEE pay on pay.ID_PAYEE = txn.ID_PAYEE 
                    left join CATEGORY cat on txn.ID_USER = cat.ID_USER and txn.ID_CATEGORY = cat.ID_CATEGORY 
                    left join TRANSFER trs_out on trs_out.ID_TRANSACTION_OUTFLOW = txn.ID_TRANSACTION and txn.TRANSACTION_FLOW = -1 
                    left join TRANSFER trs_in on trs_in.ID_TRANSACTION_INFLOW = txn.ID_TRANSACTION and txn.TRANSACTION_FLOW = 1 
                    left join TRANSACTION txn_trs_out on txn_trs_out.ID_TRANSACTION = trs_out.ID_TRANSACTION_INFLOW 
                    left join TRANSACTION txn_trs_in on txn_trs_in.ID_TRANSACTION = trs_in.ID_TRANSACTION_OUTFLOW 
                    left join ACCOUNT acc_trs_out on acc_trs_out.ID_ACCOUNT = txn_trs_out.ID_ACCOUNT 
                    left join ACCOUNT acc_trs_in on acc_trs_in.ID_ACCOUNT = txn_trs_in.ID_ACCOUNT 
                where txn.ID_USER = (%s)
                """
        values = (id_user, )
        # The following code is to handle calls where id_account is specified
        if request and request.args.get('id_account'):
            id_account = int(validate_not_empty(request, 'id_account'))
            if not account.is_valid(id_account):
                raise AccountNotFoundError
            if not account.is_valid(id_account, id_user):
                raise AccountPermissionError
            query += "and txn.ID_ACCOUNT = (%s) "
            values += (id_account,)
        return db.execute_query(query, values, fetch=True, dictionary=True)
    except ValueError:
        raise InvalidParametersError("Invalid ID account.")

def create(id_user, request):
    try:
        id_account = int(validate_not_empty(request, 'id_account'))
        flow = int(validate_not_empty(request, 'flow'))
        amount = int(validate_not_empty(request, 'amount'))
        txn_date = mysql_format_date(validate_not_empty(request, 'date'))

        if request.json.get('id_payee'):
            id_payee = int(validate_not_empty(request, 'id_payee'))
        else:
            id_payee = None
        if request.json.get('id_category'):
            id_category = int(validate_not_empty(request, 'id_category'))
        else:
            id_category = None
        if request.json.get('memo'):
            memo = validate_not_empty(request, 'memo')
        else:
            memo = None
        return sql_create(id_user, id_account, id_payee, id_category, flow, amount, txn_date, memo)
    except (ValueError, IntegrityError):
        raise InvalidParametersError

def delete(id_user, request):
    try:
        id_transaction = int(validate_not_empty(request, 'id_transaction'))
        if not is_valid(id_transaction, id_user):
            raise ValueError
        if is_transfer(id_transaction):
            id_transfer = get_transfer_id(id_transaction)
            return transfer.delete(id_user, id_transfer)
        else:
            query = "delete from TRANSACTION where ID_USER = (%s) and ID_TRANSACTION = (%s)"
            return db.execute_query(query, (id_user, id_transaction,), commit=True)
    except ValueError:
        raise InvalidParametersError

# Utilities functions
def sql_create(id_user, id_account, id_payee, id_category, flow, amount, txn_date, memo, is_transfer=0):
    query = """
            insert into TRANSACTION 
            (ID_USER, ID_ACCOUNT, ID_PAYEE, ID_CATEGORY, TRANSACTION_FLOW, TRANSACTION_AMOUNT, TRANSACTION_DATE, TRANSACTION_MEMO, IS_TRANSFER) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
    values = (id_user, id_account, id_payee, id_category, flow, amount, txn_date, memo, is_transfer)
    return db.execute_query(query, values, commit=True)

def is_transfer(id_transaction):
    query = "select IS_TRANSFER from TRANSACTION where ID_TRANSACTION = %s"
    result = db.execute_query(query, (id_transaction,), fetch=True)
    if len(result) == 0:
        raise ValueError
    if result[0][0] == 1:
        return True
    else:
        return False

def get_transfer_id(id_transaction):
    query = "select ID_TRANSFER from TRANSFER where ID_TRANSACTION_OUTFLOW = %s or ID_TRANSACTION_INFLOW = %s"
    result = db.execute_query(query, (id_transaction, id_transaction), fetch=True)
    if len(result) == 0:
        raise ValueError
    return result[0][0]

def mysql_format_date(date_string):
    return dt.datetime.strftime(dt.datetime.strptime(date_string, '%d/%m/%Y'), '%Y-%m-%d')

def is_valid(id_transaction, id_user):
    """
    This function is used to check if the provided id_transaction exists and belongs to the right id_user.
    """
    query = 'select ID_TRANSACTION from TRANSACTION where ID_TRANSACTION = %s and ID_USER = (%s)'
    result = db.execute_query(query, (id_transaction, id_user), fetch=True)
    return bool(len(result))
