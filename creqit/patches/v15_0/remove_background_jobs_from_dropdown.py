import creqit


def execute():
	item = creqit.db.exists("Navbar Item", {"item_label": "Background Jobs"})
	if not item:
		return

	creqit.delete_doc("Navbar Item", item)
