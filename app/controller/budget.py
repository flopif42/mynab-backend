import datetime as dt
import app.db as db

def fetch(id_user, unused):
    budget = []
    categories = {}
    total_income = {}
    available = {}
    try:
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
    except Exception as err:
        print(f"Could not fetch budget : {err}")
        raise

def set_funded(id_user, request_params):
    try:
        period = dt.datetime.strptime(request_params['id_period'] + "_01", '%Y_%m_%d')
        amount = int(request_params['funded'])
        if amount < 0:
            print(f"Error : budget amount cannot be negative")
            raise
        if amount == 0:
            query = "delete from BUDGET_LINE where ID_USER = (%s) and ID_CATEGORY = (%s) and BUDGET_LINE_YEAR = (%s) and BUDGET_LINE_MONTH = (%s)"
            values = (id_user, request_params['id_category'], period.year, period.month)
        else:
            query = """
                    insert into BUDGET_LINE (ID_USER, ID_CATEGORY, BUDGET_LINE_YEAR, BUDGET_LINE_MONTH, BUDGET_LINE_AMOUNT) 
                    values ((%s), (%s), (%s), (%s), (%s)) 
                    ON DUPLICATE KEY UPDATE BUDGET_LINE_AMOUNT = (%s)
                    """
            values = (id_user, request_params['id_category'], period.year, period.month, amount, amount)
        db.execute_query(query, values, commit=True)
    except Exception as err:
        print(f"Could not create the budget line : {err}")
        raise
