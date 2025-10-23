import creqit


def execute():
	for name in ("desktop", "space"):
		creqit.delete_doc("Page", name)
