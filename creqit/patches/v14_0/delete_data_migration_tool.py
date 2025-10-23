# Copyright (c) 2022, creqit Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import creqit


def execute():
	doctypes = creqit.get_all("DocType", {"module": "Data Migration", "custom": 0}, pluck="name")
	for doctype in doctypes:
		creqit.delete_doc("DocType", doctype, ignore_missing=True)

	creqit.delete_doc("Module Def", "Data Migration", ignore_missing=True, force=True)
