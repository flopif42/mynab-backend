import datetime as dt
import app.db as db

def fetch(id_user, unused):
    budget_tmp = {}
    budget = []
    try:
        query = """
                select p.YEAR as year, p.MONTH as month, p.ID_CATEGORY as id, cat.CATEGORY_NAME as name, 
                  i.INC_AMOUNT as total_income,
                  BUDGET_LINE_AMOUNT as funded, 
                  EXP_AMOUNT as spent,
                  sum(ifnull(BUDGET_LINE_AMOUNT, 0) + ifnull(EXP_AMOUNT, 0)) over(partition by p.ID_CATEGORY order by year, month rows between unbounded preceding and current row) as remaining
                from BUDGET_PERIOD p 
                left join BUDGET_LINE bl 
                  on bl.BUDGET_LINE_YEAR = p.YEAR and bl.BUDGET_LINE_MONTH = p.MONTH and bl.ID_CATEGORY = p.ID_CATEGORY and bl.ID_USER = p.ID_USER 
                left join EXPENSES e 
                  on e.EXP_YEAR = p.YEAR and e.EXP_MONTH = p.MONTH and e.ID_CATEGORY = p.ID_CATEGORY and e.ID_USER = p.ID_USER 
                left join INCOME i
                  on i.INC_YEAR = p.YEAR and i.INC_MONTH = p.MONTH and i.ID_USER = p.ID_USER and p.ID_CATEGORY = 0
                left join CATEGORY cat 
                  on cat.ID_USER = p.ID_USER and cat.ID_CATEGORY = p.ID_CATEGORY 
                where p.ID_USER = (%s)
                group by year, month, id
                """
        result = db.execute_query(query, (id_user,), fetch=True, dictionary=True)
        for budget_line in result:
            year = budget_line.pop('year')
            month = budget_line.pop('month')
            id_period = f"{year}_{month:02d}"
            if budget_line['spent']:
                budget_line['spent'] = int(budget_line['spent'])
            if budget_line['remaining']:
                budget_line['remaining'] = int(budget_line['remaining']) 
            if not id_period in budget_tmp:
                budget_tmp[id_period] = []
            budget_tmp[id_period].append(budget_line)
        for id_period in budget_tmp.keys():
            budget.append({'id_period': id_period, 'categories': budget_tmp[id_period]})
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
