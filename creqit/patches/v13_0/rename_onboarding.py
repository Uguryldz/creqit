# Copyright (c) 2020, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	if creqit.db.exists("DocType", "Onboarding"):
		creqit.rename_doc("DocType", "Onboarding", "Module Onboarding", ignore_if_exists=True)
