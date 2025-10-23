import creqit


def execute():
	creqit.reload_doc("workflow", "doctype", "workflow_transition")
	creqit.db.sql("update `tabWorkflow Transition` set allow_self_approval=1")
