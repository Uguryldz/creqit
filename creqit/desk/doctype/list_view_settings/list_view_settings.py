# Copyright (c) 2020, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit.model.document import Document


class ListViewSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from creqit.types import DF

		disable_auto_refresh: DF.Check
		disable_comment_count: DF.Check
		disable_count: DF.Check
		disable_sidebar_stats: DF.Check
		fields: DF.Code | None
		total_fields: DF.Literal["", "4", "5", "6", "7", "8", "9", "10"]
	# end: auto-generated types

	pass


@creqit.whitelist()
def save_listview_settings(doctype, listview_settings, removed_listview_fields):
	listview_settings = creqit.parse_json(listview_settings)
	removed_listview_fields = creqit.parse_json(removed_listview_fields)

	if creqit.get_all("List View Settings", filters={"name": doctype}):
		doc = creqit.get_doc("List View Settings", doctype)
		doc.update(listview_settings)
		doc.save()
	else:
		doc = creqit.new_doc("List View Settings")
		doc.name = doctype
		doc.update(listview_settings)
		doc.insert()

	set_listview_fields(doctype, listview_settings.get("fields"), removed_listview_fields)

	return {"meta": creqit.get_meta(doctype, False), "listview_settings": doc}


def set_listview_fields(doctype, listview_fields, removed_listview_fields):
	meta = creqit.get_meta(doctype)

	listview_fields = [f.get("fieldname") for f in creqit.parse_json(listview_fields) if f.get("fieldname")]

	for field in removed_listview_fields:
		set_in_list_view_property(doctype, meta.get_field(field), "0")

	for field in listview_fields:
		set_in_list_view_property(doctype, meta.get_field(field), "1")


def set_in_list_view_property(doctype, field, value):
	if not field or field.fieldname == "status_field":
		return

	property_setter = creqit.db.get_value(
		"Property Setter",
		{"doc_type": doctype, "field_name": field.fieldname, "property": "in_list_view"},
	)
	if property_setter:
		doc = creqit.get_doc("Property Setter", property_setter)
		doc.value = value
		doc.save()
	else:
		creqit.make_property_setter(
			{
				"doctype": doctype,
				"doctype_or_field": "DocField",
				"fieldname": field.fieldname,
				"property": "in_list_view",
				"value": value,
				"property_type": "Check",
			},
			ignore_validate=True,
		)


@creqit.whitelist()
def get_default_listview_fields(doctype):
	meta = creqit.get_meta(doctype)
	path = creqit.get_module_path(
		creqit.scrub(meta.module), "doctype", creqit.scrub(meta.name), creqit.scrub(meta.name) + ".json"
	)
	doctype_json = creqit.get_file_json(path)

	fields = [f.get("fieldname") for f in doctype_json.get("fields") if f.get("in_list_view")]

	if meta.title_field:
		if meta.title_field.strip() not in fields:
			fields.append(meta.title_field.strip())

	return fields
