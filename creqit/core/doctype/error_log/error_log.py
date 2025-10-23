# Copyright (c) 2015, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit.model.document import Document
from creqit.query_builder import Interval
from creqit.query_builder.functions import Now


class ErrorLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from creqit.types import DF

		error: DF.Code | None
		method: DF.Data | None
		reference_doctype: DF.Link | None
		reference_name: DF.Data | None
		seen: DF.Check
		trace_id: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.method = str(self.method)
		self.error = str(self.error)

		if len(self.method) > 140:
			self.error = f"{self.method}\n{self.error}"
			self.method = self.method[:140]

	def onload(self):
		if not self.seen and not creqit.flags.read_only:
			self.db_set("seen", 1, update_modified=0)
			creqit.db.commit()

	@staticmethod
	def clear_old_logs(days=30):
		table = creqit.qb.DocType("Error Log")
		creqit.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))


@creqit.whitelist()
def clear_error_logs():
	"""Flush all Error Logs"""
	creqit.only_for("System Manager")
	creqit.db.truncate("Error Log")
