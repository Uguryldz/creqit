import creqit
from creqit.model.rename_doc import rename_doc


def execute():
	if creqit.db.table_exists("Workflow Action") and not creqit.db.table_exists("Workflow Action Master"):
		rename_doc("DocType", "Workflow Action", "Workflow Action Master")
		creqit.reload_doc("workflow", "doctype", "workflow_action_master")
