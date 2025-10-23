# Copyright (c) 2020, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	"""Set default module for standard Web Template, if none."""
	creqit.reload_doc("website", "doctype", "Web Template Field")
	creqit.reload_doc("website", "doctype", "web_template")

	standard_templates = creqit.get_list("Web Template", {"standard": 1})
	for template in standard_templates:
		doc = creqit.get_doc("Web Template", template.name)
		if not doc.module:
			doc.module = "Website"
			doc.save()
