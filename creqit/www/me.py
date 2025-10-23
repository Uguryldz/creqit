# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit
import creqit.www.list
from creqit import _

no_cache = 1


def get_context(context):
	if creqit.session.user == "Guest":
		creqit.throw(_("You need to be logged in to access this page"), creqit.PermissionError)

	context.current_user = creqit.get_doc("User", creqit.session.user)
	context.show_sidebar = False
