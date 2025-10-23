# Copyright (c) 2022, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import creqit
from creqit.tests import IntegrationTestCase
from creqit.utils.modules import get_modules_from_all_apps_for_user


class TestConfig(IntegrationTestCase):
	def test_get_modules(self):
		creqit_modules = creqit.get_all("Module Def", filters={"app_name": "creqit"}, pluck="name")
		all_modules_data = get_modules_from_all_apps_for_user()
		all_modules = [x["module_name"] for x in all_modules_data]
		self.assertIsInstance(all_modules_data, list)
		self.assertFalse([x for x in creqit_modules if x not in all_modules])
