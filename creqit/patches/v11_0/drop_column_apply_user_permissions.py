import creqit


def execute():
	column = "apply_user_permissions"
	to_remove = ["DocPerm", "Custom DocPerm"]

	for doctype in to_remove:
		if creqit.db.table_exists(doctype):
			if column in creqit.db.get_table_columns(doctype):
				creqit.db.sql(f"alter table `tab{doctype}` drop column {column}")

	creqit.reload_doc("core", "doctype", "docperm", force=True)
	creqit.reload_doc("core", "doctype", "custom_docperm", force=True)
