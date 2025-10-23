# Copyright (c) 2020, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	if not creqit.db.table_exists("Data Import"):
		return

	meta = creqit.get_meta("Data Import")
	# if Data Import is the new one, return early
	if meta.fields[1].fieldname == "import_type":
		return

	creqit.db.sql("DROP TABLE IF EXISTS `tabData Import Legacy`")
	creqit.rename_doc("DocType", "Data Import", "Data Import Legacy")
	creqit.db.commit()
	creqit.db.sql("DROP TABLE IF EXISTS `tabData Import`")
	creqit.rename_doc("DocType", "Data Import Beta", "Data Import")
