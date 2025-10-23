# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import os

no_cache = 1

import json
import re
from urllib.parse import urlencode

import creqit
import creqit.sessions
from creqit import _
from creqit.utils.jinja_globals import is_rtl

SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
	if creqit.session.user == "Guest":
		creqit.response["status_code"] = 403
		creqit.msgprint(_("Log in to access this page."))
		creqit.redirect(f"/login?{urlencode({'redirect-to': creqit.request.path})}")

	elif creqit.db.get_value("User", creqit.session.user, "user_type", order_by=None) == "Website User":
		creqit.throw(_("You are not permitted to access this page."), creqit.PermissionError)

	try:
		boot = creqit.sessions.get()
	except Exception as e:
		raise creqit.SessionBootFailed from e

	# this needs commit
	csrf_token = creqit.sessions.get_csrf_token()

	creqit.db.commit()

	boot_json = creqit.as_json(boot, indent=None, separators=(",", ":"))

	# remove script tags from boot
	boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)

	# TODO: Find better fix
	boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)
	boot_json = json.dumps(boot_json)

	hooks = creqit.get_hooks()
	app_include_js = hooks.get("app_include_js", []) + creqit.conf.get("app_include_js", [])
	app_include_css = hooks.get("app_include_css", []) + creqit.conf.get("app_include_css", [])
	app_include_icons = hooks.get("app_include_icons", [])

	if creqit.get_system_settings("enable_telemetry") and os.getenv("creqit_SENTRY_DSN"):
		app_include_js.append("sentry.bundle.js")

	context.update(
		{
			"no_cache": 1,
			"build_version": creqit.utils.get_build_version(),
			"app_include_js": app_include_js,
			"app_include_css": app_include_css,
			"app_include_icons": app_include_icons,
			"layout_direction": "rtl" if is_rtl() else "ltr",
			"lang": creqit.local.lang,
			"sounds": hooks["sounds"],
			"boot": boot if context.get("for_mobile") else boot_json,
			"desk_theme": boot.get("desk_theme") or "Light",
			"csrf_token": csrf_token,
			"google_analytics_id": creqit.conf.get("google_analytics_id"),
			"google_analytics_anonymize_ip": creqit.conf.get("google_analytics_anonymize_ip"),
			"app_name": (
				creqit.get_website_settings("app_name") or creqit.get_system_settings("app_name") or "creqit"
			),
		}
	)

	return context
