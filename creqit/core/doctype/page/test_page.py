# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import os
import unittest
from unittest.mock import patch

import creqit
from creqit.tests import IntegrationTestCase, UnitTestCase


class UnitTestPage(UnitTestCase):
	"""
	Unit tests for Page.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestPage(IntegrationTestCase):
	def test_naming(self):
		self.assertRaises(
			creqit.NameError,
			creqit.get_doc(doctype="Page", page_name="DocType", module="Core").insert,
		)

	@unittest.skipUnless(
		os.access(creqit.get_app_path("creqit"), os.W_OK), "Only run if creqit app paths is writable"
	)
	@patch.dict(creqit.conf, {"developer_mode": 1})
	def test_trashing(self):
		page = creqit.new_doc("Page", page_name=creqit.generate_hash(), module="Core").insert()

		page.delete()
		creqit.db.commit()

		module_path = creqit.get_module_path(page.module)
		dir_path = os.path.join(module_path, "page", creqit.scrub(page.name))

		self.assertFalse(os.path.exists(dir_path))
