import glob
import json
import os

import creqit
from creqit.query_builder import DocType as _DocType


def execute():
	"""Resetting creation datetimes for DocTypes"""
	DocType = _DocType("DocType")
	doctype_jsons = glob.glob(os.path.join("..", "apps", "creqit", "creqit", "**", "doctype", "**", "*.json"))

	creqit_modules = creqit.get_all("Module Def", filters={"app_name": "creqit"}, pluck="name")
	site_doctypes = creqit.get_all(
		"DocType",
		filters={"module": ("in", creqit_modules), "custom": False},
		fields=["name", "creation"],
	)

	for dt_path in doctype_jsons:
		with open(dt_path) as f:
			try:
				file_schema = creqit._dict(json.load(f))
			except Exception:
				continue

			if not file_schema.name:
				continue

			_site_schema = [x for x in site_doctypes if x.name == file_schema.name]
			if not _site_schema:
				continue

			if file_schema.creation != _site_schema[0].creation:
				creqit.qb.update(DocType).set(DocType.creation, file_schema.creation).where(
					DocType.name == file_schema.name
				).run()
