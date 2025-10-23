# Copyright (c) 2020, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	creqit.reload_doc("email", "doctype", "Newsletter")
	creqit.db.sql(
		"""
		UPDATE tabNewsletter
		SET content_type = 'Rich Text'
	"""
	)
