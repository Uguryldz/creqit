import creqit


def execute():
	if creqit.db.table_exists("Prepared Report"):
		creqit.reload_doc("core", "doctype", "prepared_report")
		prepared_reports = creqit.get_all("Prepared Report")
		for report in prepared_reports:
			creqit.delete_doc("Prepared Report", report.name)
