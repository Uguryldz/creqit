import creqit
from creqit.model.utils.rename_field import rename_field


def execute():
	if not creqit.db.table_exists("Dashboard Chart"):
		return

	creqit.reload_doc("desk", "doctype", "dashboard_chart")

	if creqit.db.has_column("Dashboard Chart", "is_custom"):
		rename_field("Dashboard Chart", "is_custom", "use_report_chart")
