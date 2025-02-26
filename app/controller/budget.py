import app.db as db

def fetch(id_user, unused):
    budget_lines = {}
    try:
        query = (
            "select p.YEAR as year, p.MONTH as month, p.ID_CATEGORY as id_category, "
            "truncate(ifnull(BUDGET_LINE_AMOUNT, 0)/100,2) as funded, "
            "truncate(ifnull(EXP_AMOUNT, 0)/100,2) as spent "
            "from BUDGET_PERIOD p "
            "left join BUDGET_LINE bl "
	        "on bl.BUDGET_LINE_YEAR = p.YEAR and bl.BUDGET_LINE_MONTH = p.MONTH and bl.ID_CATEGORY = p.ID_CATEGORY and bl.ID_USER = p.ID_USER "
            "left join EXPENSES e "
            "on e.EXP_YEAR = p.YEAR and e.EXP_MONTH = p.MONTH and e.ID_CATEGORY = p.ID_CATEGORY and e.ID_USER = p.ID_USER "
            "where p.ID_USER = (%s) "
        )
        result = db.execute_query(query, (id_user,), fetch=True, dictionary=True)

        month_year = ()
        for budget_line in result:
            month_year = budget_line['month'], budget_line['year']
            if not month_year in budget_lines:
                budget_lines[month_year] = []
            budget_lines[month_year].append(budget_line)
        return result
    except Exception as err:
        print(f"Could not fetch budget : {err}")
        raise
