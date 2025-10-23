# Copyright (c) 2022, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit.deferred_insert import deferred_insert as _deferred_insert
from creqit.model.document import Document


class RouteHistory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from creqit.types import DF

		route: DF.Data | None
		user: DF.Link | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from creqit.query_builder import Interval
		from creqit.query_builder.functions import Now

		table = creqit.qb.DocType("Route History")
		creqit.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))


@creqit.whitelist()
def deferred_insert(routes):
	routes = [
		{
			"user": creqit.session.user,
			"route": route.get("route"),
			"creation": route.get("creation"),
		}
		for route in creqit.parse_json(routes)
	]

	_deferred_insert("Route History", routes)


@creqit.whitelist()
def frequently_visited_links():
	return creqit.get_all(
		"Route History",
		fields=["route", "count(name) as count"],
		filters={"user": creqit.session.user},
		group_by="route",
		order_by="count desc",
		limit=5,
	)
