import creqit


def execute():
	providers = creqit.get_all("Social Login Key")

	for provider in providers:
		doc = creqit.get_doc("Social Login Key", provider)
		doc.set_icon()
		doc.save()
