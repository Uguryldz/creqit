import creqit


def execute():
	if creqit.db.db_type == "mariadb":
		creqit.db.sql_ddl("alter table `tabSingles` modify column `value` longtext")
