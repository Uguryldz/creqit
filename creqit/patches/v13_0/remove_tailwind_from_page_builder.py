# Copyright (c) 2020, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	creqit.reload_doc("website", "doctype", "web_page_block")
	# remove unused templates
	creqit.delete_doc("Web Template", "Navbar with Links on Right", force=1)
	creqit.delete_doc("Web Template", "Footer Horizontal", force=1)
