# Copyright (c) 2020, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	creqit.delete_doc("DocType", "Package Publish Tool", ignore_missing=True)
	creqit.delete_doc("DocType", "Package Document Type", ignore_missing=True)
	creqit.delete_doc("DocType", "Package Publish Target", ignore_missing=True)
