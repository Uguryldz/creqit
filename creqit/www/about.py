# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit

sitemap = 1


def get_context(context):
	context.doc = creqit.get_cached_doc("About Us Settings")

	return context
