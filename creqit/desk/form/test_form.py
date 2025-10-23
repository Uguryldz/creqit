# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit
from creqit.desk.form.linked_with import get_linked_docs, get_linked_doctypes
from creqit.tests import IntegrationTestCase


class TestForm(IntegrationTestCase):
	def test_linked_with(self):
		results = get_linked_docs("Role", "System Manager", linkinfo=get_linked_doctypes("Role"))
		self.assertTrue("User" in results)
		self.assertTrue("DocType" in results)
