# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import creqit


def add_custom_field(doctype, fieldname, fieldtype="Data", options=None):
	creqit.get_doc(
		{
			"doctype": "Custom Field",
			"dt": doctype,
			"fieldname": fieldname,
			"fieldtype": fieldtype,
			"options": options,
		}
	).insert()


def clear_custom_fields(doctype):
	creqit.db.delete("Custom Field", {"dt": doctype})
	creqit.clear_cache(doctype=doctype)
