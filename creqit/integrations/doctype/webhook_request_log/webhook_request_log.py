# Copyright (c) 2021, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit.model.document import Document


class WebhookRequestLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from creqit.types import DF

		data: DF.Code | None
		error: DF.Text | None
		headers: DF.Code | None
		reference_doctype: DF.Data | None
		reference_document: DF.Data | None
		response: DF.Code | None
		url: DF.Data | None
		user: DF.Link | None
		webhook: DF.Link | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from creqit.query_builder import Interval
		from creqit.query_builder.functions import Now

		table = creqit.qb.DocType("Webhook Request Log")
		creqit.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))
