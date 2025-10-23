# Copyright (c) 2021, creqit Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import creqit


def execute():
	creqit.reload_doc("website", "doctype", "web_form_list_column")
	creqit.reload_doctype("Web Form")

	for web_form in creqit.get_all("Web Form", fields=["*"]):
		if web_form.allow_multiple and not web_form.show_list:
			creqit.db.set_value("Web Form", web_form.name, "show_list", True)
