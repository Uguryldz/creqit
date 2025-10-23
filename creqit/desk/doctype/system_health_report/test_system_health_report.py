# Copyright (c) 2024, creqit Technologies and Contributors
# See license.txt

import creqit
from creqit.tests import IntegrationTestCase, UnitTestCase


class UnitTestSystemHealthReport(UnitTestCase):
	"""
	Unit tests for SystemHealthReport.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestSystemHealthReport(IntegrationTestCase):
	def test_it_works(self):
		creqit.get_doc("System Health Report")
