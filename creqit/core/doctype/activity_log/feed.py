# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit
import creqit.permissions
from creqit import _
from creqit.core.doctype.activity_log.activity_log import add_authentication_log
from creqit.utils import get_fullname


def login_feed(login_manager):
	if login_manager.user != "Guest":
		subject = _("{0} logged in").format(get_fullname(login_manager.user))
		add_authentication_log(subject, login_manager.user)


def logout_feed(user, reason):
	if user and user != "Guest":
		subject = _("{0} logged out: {1}").format(get_fullname(user), creqit.bold(reason))
		add_authentication_log(subject, user, operation="Logout")
