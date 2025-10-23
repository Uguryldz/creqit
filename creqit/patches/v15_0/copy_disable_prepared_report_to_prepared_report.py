import creqit


def execute():
	table = creqit.qb.DocType("Report")
	creqit.qb.update(table).set(table.prepared_report, 0).where(table.disable_prepared_report == 1)
