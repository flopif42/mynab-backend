import app.db as db

def fetch(id_user, unused):
    budget_tmp = {}
    budget = []
    try:
        query = (
            "select p.YEAR as year, p.MONTH as month, p.ID_CATEGORY as id, cat.CATEGORY_NAME "
            "truncate(ifnull(BUDGET_LINE_AMOUNT, 0)/100,2) as funded, "
            "truncate(ifnull(EXP_AMOUNT, 0)/100,2) as spent "
            "from BUDGET_PERIOD p "
            "left join BUDGET_LINE bl "
	        "on bl.BUDGET_LINE_YEAR = p.YEAR and bl.BUDGET_LINE_MONTH = p.MONTH and bl.ID_CATEGORY = p.ID_CATEGORY and bl.ID_USER = p.ID_USER "
            "left join EXPENSES e "
            "on e.EXP_YEAR = p.YEAR and e.EXP_MONTH = p.MONTH and e.ID_CATEGORY = p.ID_CATEGORY and e.ID_USER = p.ID_USER "
            "left join CATEGORY cat "
            "on cat.ID_USER = p.ID_USER and cat.ID_CATEGORY = p.ID_CATEGORY "
            "where p.ID_USER = (%s) "
        )
        result = db.execute_query(query, (id_user,), fetch=True, dictionary=True)
        for budget_line in result:
            year = budget_line.pop('year')
            month = budget_line.pop('month')
            id_month = f"{year}_{month:02d}"
            if not id_month in budget_tmp:
                budget_tmp[id_month] = []
            budget_tmp[id_month].append(budget_line)
        for id_month in budget_tmp.keys():
            budget.append({'id_month': id_month, 'categories': budget_tmp[id_month]})
        return budget
    except Exception as err:
        print(f"Could not fetch budget : {err}")
        raise
