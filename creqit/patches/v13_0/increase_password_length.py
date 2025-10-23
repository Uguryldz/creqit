import creqit


def execute():
	creqit.db.change_column_type("__Auth", column="password", type="TEXT")
