import creqit


def execute():
	creqit.reload_doc("core", "doctype", "doctype_link")
	creqit.reload_doc("core", "doctype", "doctype_action")
	creqit.reload_doc("core", "doctype", "doctype")
	creqit.model.delete_fields({"DocType": ["hide_heading", "image_view", "read_only_onload"]}, delete=1)

	creqit.db.delete("Property Setter", {"property": "read_only_onload"})
