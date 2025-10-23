# Copyright (c) 2015, creqit Technologies and Contributors
# License: MIT. See LICENSE
import time

import creqit
from creqit.auth import CookieManager, LoginManager
from creqit.tests import IntegrationTestCase, UnitTestCase


class UnitTestActivityLog(UnitTestCase):
	"""
	Unit tests for ActivityLog.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestActivityLog(IntegrationTestCase):
	def setUp(self) -> None:
		creqit.set_user("Administrator")

	def test_activity_log(self):
		# test user login log
		creqit.local.form_dict = creqit._dict(
			{
				"cmd": "login",
				"sid": "Guest",
				"pwd": self.ADMIN_PASSWORD or "admin",
				"usr": "Administrator",
			}
		)

		creqit.local.request_ip = "127.0.0.1"
		creqit.local.cookie_manager = CookieManager()
		creqit.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertFalse(creqit.form_dict.pwd)
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		creqit.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		creqit.form_dict.update({"pwd": "password"})
		self.assertRaises(creqit.AuthenticationError, LoginManager)
		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Failed")

		creqit.local.form_dict = creqit._dict()

	def get_auth_log(self, operation="Login"):
		names = creqit.get_all(
			"Activity Log",
			filters={
				"user": "Administrator",
				"operation": operation,
			},
			order_by="`creation` DESC",
		)

		name = names[0]
		return creqit.get_doc("Activity Log", name)

	def test_brute_security(self):
		update_system_settings({"allow_consecutive_login_attempts": 3, "allow_login_after_fail": 5})

		creqit.local.form_dict = creqit._dict(
			{"cmd": "login", "sid": "Guest", "pwd": self.ADMIN_PASSWORD, "usr": "Administrator"}
		)

		creqit.local.request_ip = "127.0.0.1"
		creqit.local.cookie_manager = CookieManager()
		creqit.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		creqit.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		creqit.form_dict.update({"pwd": "password"})
		self.assertRaises(creqit.AuthenticationError, LoginManager)
		self.assertRaises(creqit.AuthenticationError, LoginManager)
		self.assertRaises(creqit.AuthenticationError, LoginManager)

		# REMOVE ME: current logic allows allow_consecutive_login_attempts+1 attempts
		# before raising security exception, remove below line when that is fixed.
		self.assertRaises(creqit.AuthenticationError, LoginManager)
		self.assertRaises(creqit.SecurityException, LoginManager)
		time.sleep(5)
		self.assertRaises(creqit.AuthenticationError, LoginManager)

		creqit.local.form_dict = creqit._dict()


def update_system_settings(args):
	doc = creqit.get_doc("System Settings")
	doc.update(args)
	doc.flags.ignore_mandatory = 1
	doc.save()
