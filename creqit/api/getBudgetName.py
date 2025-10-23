import jwt

from datetime import timedelta
from creqit.utils import now_datetime
import creqit

@creqit.whitelist()
def getBudgetName(doctype, txt, searchfield, start, page_len, filters):
    # Filtreler varsa, sorguya ekliyoruz
    conditions = ""
    if filters.get("budget_name_filter"):
        conditions += " AND budget_name = %(budget_name_filter)s"
    
    # Create Budget'dan distinct budget_name'leri çekiyoruz
    return creqit.db.sql("""
        SELECT DISTINCT budget_name
        FROM `tabCreate Budget`
        WHERE budget_name LIKE %(txt)s
        {conditions}
        ORDER BY budget_name
        LIMIT 20
    """.format(conditions=conditions), {"txt": "%" + txt + "%", "budget_name_filter": filters.get("budget_name_filter")})
