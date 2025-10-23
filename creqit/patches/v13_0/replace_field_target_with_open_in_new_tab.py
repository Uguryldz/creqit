import creqit


def execute():
	doctype = "Top Bar Item"
	if not creqit.db.table_exists(doctype) or not creqit.db.has_column(doctype, "target"):
		return

	creqit.reload_doc("website", "doctype", "top_bar_item")
	creqit.db.set_value(doctype, {"target": 'target = "_blank"'}, "open_in_new_tab", 1)
