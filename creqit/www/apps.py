# Copyright (c) 2023, creqit Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import creqit
from creqit import _
from creqit.apps import get_apps


def get_context():
	all_apps = get_apps()

	system_default_app = creqit.get_system_settings("default_app")
	user_default_app = creqit.db.get_value("User", creqit.session.user, "default_app")
	default_app = user_default_app if user_default_app else system_default_app

	if len(all_apps) == 0:
		creqit.local.flags.redirect_location = "/app"
		raise creqit.Redirect

	for app in all_apps:
		app["is_default"] = True if app.get("name") == default_app else False

	return {"apps": all_apps}
