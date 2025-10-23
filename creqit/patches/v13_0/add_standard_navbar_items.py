import creqit
from creqit.utils.install import add_standard_navbar_items


def execute():
	# Add standard navbar items for creqit in Navbar Settings
	creqit.reload_doc("core", "doctype", "navbar_settings")
	creqit.reload_doc("core", "doctype", "navbar_item")
	add_standard_navbar_items()
