import app.db as db

def fetch(id_user, unused):
    try:
        query = (
            "select p.ID_USER, p.YEAR, p.MONTH, p.ID_CATEGORY, cat.CATEGORY_NAME, BUDGET_LINE_AMOUNT, EXP_AMOUNT "
            "from BUDGET_PERIOD p "
            "left join BUDGET_LINE bl "
	        "on bl.BUDGET_LINE_YEAR = p.YEAR and bl.BUDGET_LINE_MONTH = p.MONTH "
            "and bl.ID_CATEGORY = p.ID_CATEGORY and bl.ID_USER = p.ID_USER "
            "left join EXPENSES e "
            "on e.EXP_YEAR = p.YEAR and e.EXP_MONTH = p.MONTH "
            "and e.ID_CATEGORY = p.ID_CATEGORY and e.ID_USER = p.ID_USER "
            "left join CATEGORY cat "
            "on cat.ID_USER = p.ID_USER and cat.ID_CATEGORY = p.ID_CATEGORY "
            "where p.ID_USER = (%s) "
        )
        result = db.execute_query(query, (id_user,), fetch=True, dictionary=True)
        return result
    except Exception as err:
        print(f"Could not fetch budget : {err}")
        raise
