import creqit
from creqit.model.rename_doc import rename_doc


def execute():
	if creqit.db.table_exists("Standard Reply") and not creqit.db.table_exists("Email Template"):
		rename_doc("DocType", "Standard Reply", "Email Template")
		creqit.reload_doc("email", "doctype", "email_template")
