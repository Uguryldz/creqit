# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	creqit.reload_doc("core", "doctype", "system_settings", force=1)
	creqit.db.set_single_value("System Settings", "password_reset_limit", 3)
