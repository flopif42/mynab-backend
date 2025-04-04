import datetime as dt
from mysql.connector.errors import IntegrityError
from app.sql_manager import SqlManager as db
from http import HTTPStatus
from app.exceptions import OperationError
from app.utils import validate_not_empty

def list(id_user, request_unused):
    budget = []
    categories = {}
    total_income = {}
    available = {}

    query = """
            select p.YEAR as year, p.MONTH as month, cat.ID_CATEGORY as id,
                ifnull(i.INC_AMOUNT, 0) as total_income, ifnull(atb.available, 0) as available,
                bl.BUDGET_LINE_AMOUNT as funded, e.EXP_AMOUNT as spent,
                sum(ifnull(BUDGET_LINE_AMOUNT, 0) + ifnull(EXP_AMOUNT, 0)) over(partition by cat.ID_CATEGORY order by year, month rows between unbounded preceding and current row) as remaining
            from BUDGET_PERIOD p
            left join CATEGORY cat
	            on cat.ID_USER = p.ID_USER
            left join AVAILABLE_TO_BUDGET atb
                on atb.ID_USER = p.ID_USER and atb.YEAR = p.YEAR and atb.month = p.MONTH and cat.ID_CATEGORY = 0
            left join EXPENSES e
	            on e.ID_USER = p.ID_USER and e.EXP_YEAR = p.YEAR and e.EXP_MONTH = p.MONTH and e.ID_CATEGORY = cat.ID_CATEGORY
            left join INCOME i
                on i.ID_USER = p.ID_USER and i.INC_YEAR = p.YEAR and i.INC_MONTH = p.MONTH and cat.ID_CATEGORY = 0
            left join BUDGET_LINE bl
                on bl.ID_USER = p.ID_USER and bl.BUDGET_LINE_YEAR = p.YEAR and bl.BUDGET_LINE_MONTH = p.MONTH and bl.ID_CATEGORY = cat.ID_CATEGORY
            where p.ID_USER = (%s)
            """
    result = db.execute_query(query, (id_user,), fetch=True, dictionary=True)
    for row in result:
        year = row.pop('year')
        month = row.pop('month')
        id_period = f"{year}_{month:02d}"
        if not id_period in categories:
            categories[id_period] = []
        if row['id'] == 0: # Manage income values (total income for the month and available to budget)
            total_income[id_period] = row['total_income']
            available[id_period] = row['available']
        else: # Manage budget values (funded, spent and remaining)
            row.pop('total_income')
            row.pop('available')
            if row['spent']:
                row['spent'] = int(row['spent'])
            row['remaining'] = int(row['remaining']) 
            categories[id_period].append(row)

    for id_period in categories.keys():
        budget.append({
            'id_period': id_period,
            'total_income': int(total_income[id_period]),
            'available': int(available[id_period]),
            'categories': categories[id_period]
        })
    return budget

def set_funded(id_user, request):
    try:
        id_period = validate_not_empty(request, 'id_period')
        amount = int(validate_not_empty(request, 'amount'))
        id_category = int(validate_not_empty(request, 'id_category'))

        period = dt.datetime.strptime(id_period + "_01", '%Y_%m_%d')
        if amount < 0:
            raise OperationError(HTTPStatus.BAD_REQUEST, "Amount must be a positive integer.")
        if amount == 0:
            query = "delete from BUDGET_LINE where ID_USER = (%s) and ID_CATEGORY = (%s) and BUDGET_LINE_YEAR = (%s) and BUDGET_LINE_MONTH = (%s)"
            values = (id_user, id_category, period.year, period.month)
        else:
            query = """
                    insert into BUDGET_LINE (ID_USER, ID_CATEGORY, BUDGET_LINE_YEAR, BUDGET_LINE_MONTH, BUDGET_LINE_AMOUNT) 
                    values ((%s), (%s), (%s), (%s), (%s)) 
                    ON DUPLICATE KEY UPDATE BUDGET_LINE_AMOUNT = (%s)
                    """
            values = (id_user, id_category, period.year, period.month, amount, amount)
        db.execute_query(query, values, commit=True)
    except ValueError:
        raise OperationError(HTTPStatus.BAD_REQUEST, "Invalid parameters.")
    except IntegrityError:
        raise OperationError(HTTPStatus.BAD_REQUEST, "Some parameters are incorrect.")
