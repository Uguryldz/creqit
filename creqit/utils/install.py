# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import getpass

import creqit
from creqit.geo.doctype.country.country import import_country_and_currency
from creqit.utils import cint
from creqit.utils.password import update_password


def before_install():
	creqit.reload_doc("core", "doctype", "doctype_state")
	creqit.reload_doc("core", "doctype", "docfield")
	creqit.reload_doc("core", "doctype", "docperm")
	creqit.reload_doc("core", "doctype", "doctype_action")
	creqit.reload_doc("core", "doctype", "doctype_link")
	creqit.reload_doc("desk", "doctype", "form_tour_step")
	creqit.reload_doc("desk", "doctype", "form_tour")
	creqit.reload_doc("core", "doctype", "doctype")
	creqit.clear_cache()


def after_install():
	create_user_type()
	install_basic_docs()

	from creqit.core.doctype.file.utils import make_home_folder
	from creqit.core.doctype.language.language import sync_languages

	make_home_folder()
	import_country_and_currency()
	sync_languages()

	# save default print setting
	print_settings = creqit.get_doc("Print Settings")
	print_settings.save()

	# all roles to admin
	creqit.get_doc("User", "Administrator").add_roles(*creqit.get_all("Role", pluck="name"))

	# update admin password
	update_password("Administrator", get_admin_password())

	if not creqit.conf.skip_setup_wizard:
		# only set home_page if the value doesn't exist in the db
		if not creqit.db.get_default("desktop:home_page"):
			creqit.db.set_default("desktop:home_page", "setup-wizard")
			creqit.db.set_single_value("System Settings", "setup_complete", 0)

	# clear test log
	from creqit.tests.utils.generators import _after_install_clear_test_log

	_after_install_clear_test_log()

	add_standard_navbar_items()

	creqit.db.commit()


def create_user_type():
	for user_type in ["System User", "Website User"]:
		if not creqit.db.exists("User Type", user_type):
			creqit.get_doc({"doctype": "User Type", "name": user_type, "is_standard": 1}).insert(
				ignore_permissions=True
			)


def install_basic_docs():
	# core users / roles
	install_docs = [
		{
			"doctype": "User",
			"name": "Administrator",
			"first_name": "Administrator",
			"email": "admin@example.com",
			"enabled": 1,
			"is_admin": 1,
			"roles": [{"role": "Administrator"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{
			"doctype": "User",
			"name": "Guest",
			"first_name": "Guest",
			"email": "guest@example.com",
			"enabled": 1,
			"is_guest": 1,
			"roles": [{"role": "Guest"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{"doctype": "Role", "role_name": "Report Manager"},
		{"doctype": "Role", "role_name": "Translator"},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Pending",
			"icon": "question-sign",
			"style": "",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Approved",
			"icon": "ok-sign",
			"style": "Success",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Rejected",
			"icon": "remove",
			"style": "Danger",
		},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Approve"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Reject"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Review"},
		{
			"doctype": "Email Domain",
			"domain_name": "example.com",
			"email_id": "account@example.com",
			"password": "pass",
			"email_server": "imap.example.com",
			"use_imap": 1,
			"smtp_server": "smtp.example.com",
		},
		{
			"doctype": "Email Account",
			"domain": "example.com",
			"email_id": "notifications@example.com",
			"default_outgoing": 1,
		},
		{
			"doctype": "Email Account",
			"domain": "example.com",
			"email_id": "replies@example.com",
			"default_incoming": 1,
		},
	]

	for d in install_docs:
		try:
			creqit.get_doc(d).insert(ignore_if_duplicate=True)
		except creqit.NameError:
			pass


def get_admin_password():
	return creqit.conf.get("admin_password") or getpass.getpass("Set Administrator password: ")


def before_tests():
	if len(creqit.get_installed_apps()) > 1:
		# don't run before tests if any other app is installed
		return

	creqit.db.truncate("Custom Field")
	creqit.db.truncate("Event")

	creqit.clear_cache()

	# complete setup if missing
	if not cint(creqit.db.get_single_value("System Settings", "setup_complete")):
		complete_setup_wizard()

	creqit.db.set_single_value("Website Settings", "disable_signup", 0)
	creqit.db.commit()
	creqit.clear_cache()


def complete_setup_wizard():
	from creqit.desk.page.setup_wizard.setup_wizard import setup_complete

	setup_complete(
		{
			"language": "English",
			"email": "test@creqit.com",
			"full_name": "Test User",
			"password": "test",
			"country": "United States",
			"timezone": "America/New_York",
			"currency": "USD",
			"enable_telemtry": 1,
		}
	)


def add_standard_navbar_items():
	navbar_settings = creqit.get_single("Navbar Settings")

	# don't add settings/help options if they're already present
	if navbar_settings.settings_dropdown and navbar_settings.help_dropdown:
		return

	navbar_settings.settings_dropdown = []
	navbar_settings.help_dropdown = []

	for item in creqit.get_hooks("standard_navbar_items"):
		navbar_settings.append("settings_dropdown", item)

	for item in creqit.get_hooks("standard_help_items"):
		navbar_settings.append("help_dropdown", item)

	navbar_settings.save()
