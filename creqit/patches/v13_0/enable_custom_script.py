# Copyright (c) 2020, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	"""Enable all the existing Client script"""

	creqit.db.sql(
		"""
		UPDATE `tabClient Script` SET enabled=1
	"""
	)
