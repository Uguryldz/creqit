import creqit


def execute():
	creqit.reload_doc("desk", "doctype", "dashboard_chart")

	if not creqit.db.table_exists("Dashboard Chart"):
		return

	users_with_permission = creqit.get_all(
		"Has Role",
		fields=["parent"],
		filters={"role": ["in", ["System Manager", "Dashboard Manager"]], "parenttype": "User"},
		distinct=True,
	)

	users = [item.parent for item in users_with_permission]
	charts = creqit.get_all("Dashboard Chart", filters={"owner": ["in", users]})

	for chart in charts:
		creqit.db.set_value("Dashboard Chart", chart.name, "is_public", 1)
