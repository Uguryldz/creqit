import creqit
from creqit.model.rename_doc import rename_doc


def execute():
	if creqit.db.table_exists("Email Alert Recipient") and not creqit.db.table_exists(
		"Notification Recipient"
	):
		rename_doc("DocType", "Email Alert Recipient", "Notification Recipient")
		creqit.reload_doc("email", "doctype", "notification_recipient")

	if creqit.db.table_exists("Email Alert") and not creqit.db.table_exists("Notification"):
		rename_doc("DocType", "Email Alert", "Notification")
		creqit.reload_doc("email", "doctype", "notification")
