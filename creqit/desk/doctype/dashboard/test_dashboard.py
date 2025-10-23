# Copyright (c) 2019, creqit Technologies and Contributors
# License: MIT. See LICENSE
import creqit
from creqit.core.doctype.user.test_user import test_user
from creqit.tests import IntegrationTestCase, UnitTestCase
from creqit.utils.modules import get_modules_from_all_apps_for_user


class UnitTestDashboard(UnitTestCase):
	"""
	Unit tests for Dashboard.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestDashboard(IntegrationTestCase):
	def test_permission_query(self):
		for user in ["Administrator", "test@example.com"]:
			with self.set_user(user):
				creqit.get_list("Dashboard")

		with test_user(roles=["_Test Role"]) as user:
			with self.set_user(user.name):
				creqit.get_list("Dashboard")
				with self.set_user("Administrator"):
					all_modules = get_modules_from_all_apps_for_user("Administrator")
					for module in all_modules:
						user.append("block_modules", {"module": module.get("module_name")})
					user.save()
				creqit.get_list("Dashboard")
