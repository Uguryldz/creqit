import creqit


def execute():
	categories = creqit.get_list("Blog Category")
	for category in categories:
		doc = creqit.get_doc("Blog Category", category["name"])
		doc.set_route()
		doc.save()
