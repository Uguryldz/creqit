# Copyright (c) 2018, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	signatures = creqit.db.get_list("User", {"email_signature": ["!=", ""]}, ["name", "email_signature"])
	creqit.reload_doc("core", "doctype", "user")
	for d in signatures:
		signature = d.get("email_signature")
		signature = signature.replace("\n", "<br>")
		signature = "<div>" + signature + "</div>"
		creqit.db.set_value("User", d.get("name"), "email_signature", signature)
