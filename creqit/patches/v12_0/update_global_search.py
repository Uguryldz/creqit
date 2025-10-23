import creqit
from creqit.desk.page.setup_wizard.install_fixtures import update_global_search_doctypes


def execute():
	creqit.reload_doc("desk", "doctype", "global_search_doctype")
	creqit.reload_doc("desk", "doctype", "global_search_settings")
	update_global_search_doctypes()
