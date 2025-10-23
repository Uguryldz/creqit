# Copyright (c) 2020, creqit Technologies and contributors
# License: MIT. See LICENSE

import json

import creqit

# import creqit
from creqit.model.document import Document


class DashboardSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from creqit.types import DF

		chart_config: DF.Code | None
		user: DF.Link | None
	# end: auto-generated types

	pass


@creqit.whitelist()
def create_dashboard_settings(user):
	if not creqit.db.exists("Dashboard Settings", user):
		doc = creqit.new_doc("Dashboard Settings")
		doc.name = user
		doc.insert(ignore_permissions=True)
		creqit.db.commit()
		return doc


def get_permission_query_conditions(user):
	if not user:
		user = creqit.session.user

	return f"""(`tabDashboard Settings`.name = {creqit.db.escape(user)})"""


@creqit.whitelist()
def save_chart_config(reset, config, chart_name):
	reset = creqit.parse_json(reset)
	doc = creqit.get_doc("Dashboard Settings", creqit.session.user)
	chart_config = creqit.parse_json(doc.chart_config) or {}

	if reset:
		chart_config[chart_name] = {}
	else:
		config = creqit.parse_json(config)
		if chart_name not in chart_config:
			chart_config[chart_name] = {}
		chart_config[chart_name].update(config)

	creqit.db.set_value("Dashboard Settings", creqit.session.user, "chart_config", json.dumps(chart_config))
