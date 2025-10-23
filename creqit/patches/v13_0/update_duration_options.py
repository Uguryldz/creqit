# Copyright (c) 2020, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	creqit.reload_doc("core", "doctype", "DocField")

	if creqit.db.has_column("DocField", "show_days"):
		creqit.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_days = 1 WHERE show_days = 0
		"""
		)
		creqit.db.sql_ddl("alter table tabDocField drop column show_days")

	if creqit.db.has_column("DocField", "show_seconds"):
		creqit.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_seconds = 1 WHERE show_seconds = 0
		"""
		)
		creqit.db.sql_ddl("alter table tabDocField drop column show_seconds")

	creqit.clear_cache(doctype="DocField")
