# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


@creqit.whitelist()
def get(name):
	"""
	Return the :term:`doclist` of the `Page` specified by `name`
	"""
	page = creqit.get_doc("Page", name)
	if page.is_permitted():
		page.load_assets()
		docs = creqit._dict(page.as_dict())
		if getattr(page, "_dynamic_page", None):
			docs["_dynamic_page"] = 1

		return docs
	else:
		creqit.response["403"] = 1
		raise creqit.PermissionError("No read permission for Page %s" % (page.title or name))


@creqit.whitelist(allow_guest=True)
def getpage():
	"""
	Load the page from `creqit.form` and send it via `creqit.response`
	"""
	page = creqit.form_dict.get("name")
	doc = get(page)

	creqit.response.docs.append(doc)
