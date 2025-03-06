import datetime as dt
from app.sql_manager import SqlManager
from app.controller import payee, account, child_category, parent_category, transfer

def fetch_all(id_user, request_params):
    try:
        query = (
            "select acc.ACCOUNT_NAME as account, "
            "txn.ID_TRANSACTION as id, "
            "case "
            "when (txn.IS_TRANSFER=1 and txn.TRANSACTION_FLOW = -1) then concat('Transfer to: ', acc_trs_out.ACCOUNT_NAME) "
            "when (txn.IS_TRANSFER=1 and txn.TRANSACTION_FLOW = 1) then concat('Transfer from: ', acc_trs_in.ACCOUNT_NAME) "
            "else PAYEE_NAME end as payee, "
            "CATEGORY_NAME as category, "
            "if(txn.TRANSACTION_FLOW=-1, 'Outflow', 'Inflow') as flow, "
            "txn.TRANSACTION_AMOUNT as amount, "
            "date_format(txn.TRANSACTION_DATE, \"%d/%m/%Y\") as date, "
            "txn.TRANSACTION_MEMO as memo "
            "from TRANSACTION txn "
            "inner join ACCOUNT acc on acc.ID_ACCOUNT = txn.ID_ACCOUNT "
            "left join PAYEE pay on pay.ID_PAYEE = txn.ID_PAYEE "
            "left join CATEGORY cat on txn.ID_USER = cat.ID_USER and txn.ID_CATEGORY = cat.ID_CATEGORY "
            "left join TRANSFER trs_out on trs_out.ID_TRANSACTION_OUTFLOW = txn.ID_TRANSACTION and txn.TRANSACTION_FLOW = -1 "
            "left join TRANSFER trs_in on trs_in.ID_TRANSACTION_INFLOW = txn.ID_TRANSACTION and txn.TRANSACTION_FLOW = 1 "
            "left join TRANSACTION txn_trs_out on txn_trs_out.ID_TRANSACTION = trs_out.ID_TRANSACTION_INFLOW "
            "left join TRANSACTION txn_trs_in on txn_trs_in.ID_TRANSACTION = trs_in.ID_TRANSACTION_OUTFLOW "
            "left join ACCOUNT acc_trs_out on acc_trs_out.ID_ACCOUNT = txn_trs_out.ID_ACCOUNT "
            "left join ACCOUNT acc_trs_in on acc_trs_in.ID_ACCOUNT = txn_trs_in.ID_ACCOUNT "
            "where txn.ID_USER = (%s) "
        )
        if (not request_params is None) and ('id_account' in request_params) and (not request_params['id_account'] is None):
            query = query + "and txn.ID_ACCOUNT = (%s) "
            values = (str(id_user), request_params['id_account'])
        else:
            values = (str(id_user), )
        result = SqlManager.execute_query(query, values, fetch=True, dictionary=True)
        return result
    except Exception as err:
        print(f"Could not fetch transactions : {err}")
        raise

def create(id_user, request_params):
    # request_params contains the following :
    # id_account, id_payee, flow, amount, date, memo

    if ('id_payee' in request_params) and (request_params['id_payee'] != ''):
        id_payee = request_params['id_payee']
    else:
        id_payee = None
    
    if ('id_category' in request_params) and (request_params['id_category'] != ''):
        id_category = request_params['id_category']
    else:
        id_category = None

    try:
        txn_date = mysql_format_date(request_params['date'])
        query = (
            "insert into TRANSACTION "
            "(ID_USER, ID_ACCOUNT, ID_PAYEE, ID_CATEGORY, TRANSACTION_FLOW, TRANSACTION_AMOUNT, TRANSACTION_DATE, TRANSACTION_MEMO, IS_TRANSFER) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        values = (id_user, request_params['id_account'], id_payee, id_category, request_params['flow'], request_params['amount'], txn_date, request_params['memo'], request_params['is_transfer'])
        result = SqlManager.execute_query(query, values, commit=True)
        return result
    except Exception as err:
        print(f"Could not add the transaction : {err}")
        raise

def delete(id_user, request_params):
    try:
        id_transaction = request_params['id_transaction']
        if is_transfer(id_transaction):
            id_transfer = get_transfer_id(id_transaction)
            return transfer.delete(id_user, id_transfer)
        else:
            query = "delete from TRANSACTION where ID_USER = (%s) and ID_TRANSACTION = (%s)"
            return SqlManager.execute_query(query, (id_user, id_transaction,), commit=True)
    except Exception as err:
        print(f"Exception: {err}")
        return None

# Utilities functions
def is_transfer(id_transaction):
    query = "select IS_TRANSFER from TRANSACTION where ID_TRANSACTION = %s"
    result = SqlManager.execute_query(query, (id_transaction,), fetch=True)
    if result[0][0] == 1:
        return True
    else:
        return False

def get_transfer_id(id_transaction):
    query = (
        "select ID_TRANSFER from TRANSFER "
        "where ID_TRANSACTION_OUTFLOW = %s or ID_TRANSACTION_INFLOW = %s"
    )
    result = SqlManager.execute_query(query, (id_transaction, id_transaction), fetch=True)
    if len(result) > 0:
        return result[0][0]

def mysql_format_date(date_string):
    return dt.datetime.strftime(dt.datetime.strptime(date_string, '%d/%m/%Y'), '%Y-%m-%d')
