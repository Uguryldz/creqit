import creqit


def execute():
	"""
	Rename the Marketing Campaign table to UTM Campaign table
	"""
	if creqit.db.exists("DocType", "UTM Campaign"):
		return
	creqit.rename_doc("DocType", "Marketing Campaign", "UTM Campaign", force=True)
	creqit.reload_doctype("UTM Campaign", force=True)
