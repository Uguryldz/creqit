# Copyright (c) 2015, creqit Technologies and Contributors
# License: MIT. See LICENSE
import creqit
from creqit.contacts.doctype.address_template.address_template import get_default_address_template
from creqit.tests import IntegrationTestCase, UnitTestCase
from creqit.utils.jinja import validate_template


class UnitTestAddressTemplate(UnitTestCase):
	"""
	Unit tests for AddressTemplate.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestAddressTemplate(IntegrationTestCase):
	def setUp(self) -> None:
		creqit.db.delete("Address Template", {"country": "India"})
		creqit.db.delete("Address Template", {"country": "Brazil"})

	def test_default_address_template(self):
		validate_template(get_default_address_template())

	def test_default_is_unset(self):
		creqit.get_doc({"doctype": "Address Template", "country": "India", "is_default": 1}).insert()

		self.assertEqual(creqit.db.get_value("Address Template", "India", "is_default"), 1)

		creqit.get_doc({"doctype": "Address Template", "country": "Brazil", "is_default": 1}).insert()

		self.assertEqual(creqit.db.get_value("Address Template", "India", "is_default"), 0)
		self.assertEqual(creqit.db.get_value("Address Template", "Brazil", "is_default"), 1)

	def test_delete_address_template(self):
		india = creqit.get_doc({"doctype": "Address Template", "country": "India", "is_default": 0}).insert()

		brazil = creqit.get_doc(
			{"doctype": "Address Template", "country": "Brazil", "is_default": 1}
		).insert()

		india.reload()  # might have been modified by the second template
		india.delete()  # should not raise an error

		self.assertRaises(creqit.ValidationError, brazil.delete)
