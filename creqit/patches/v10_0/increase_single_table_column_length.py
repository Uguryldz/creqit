"""
Run this after updating country_info.json and or
"""
import creqit


def execute():
	for col in ("field", "doctype"):
		creqit.db.sql_ddl(f"alter table `tabSingles` modify column `{col}` varchar(255)")
