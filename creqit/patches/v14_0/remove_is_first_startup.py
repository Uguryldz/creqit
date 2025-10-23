import creqit


def execute():
	singles = creqit.qb.Table("tabSingles")
	creqit.qb.from_(singles).delete().where(
		(singles.doctype == "System Settings") & (singles.field == "is_first_startup")
	).run()
