# Copyright (c) 2022, creqit and Contributors
# License: MIT. See LICENSE


import creqit
from creqit.model import data_field_options


def execute():
	custom_field = creqit.qb.DocType("Custom Field")
	(
		creqit.qb.update(custom_field)
		.set(custom_field.options, None)
		.where((custom_field.fieldtype == "Data") & (custom_field.options.notin(data_field_options)))
	).run()
