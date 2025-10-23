import creqit
from creqit.model.rename_doc import rename_doc


def execute():
	if creqit.db.exists("DocType", "Client Script"):
		return

	creqit.flags.ignore_route_conflict_validation = True
	rename_doc("DocType", "Custom Script", "Client Script")
	creqit.flags.ignore_route_conflict_validation = False

	creqit.reload_doctype("Client Script", force=True)
