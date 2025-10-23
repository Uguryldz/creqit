# Copyright (c) 2019, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit.model.document import Document


class NotificationSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from creqit.desk.doctype.notification_subscribed_document.notification_subscribed_document import (
			NotificationSubscribedDocument,
		)
		from creqit.types import DF

		enable_email_assignment: DF.Check
		enable_email_energy_point: DF.Check
		enable_email_event_reminders: DF.Check
		enable_email_mention: DF.Check
		enable_email_notifications: DF.Check
		enable_email_share: DF.Check
		enable_email_threads_on_assigned_document: DF.Check
		enabled: DF.Check
		energy_points_system_notifications: DF.Check
		seen: DF.Check
		subscribed_documents: DF.TableMultiSelect[NotificationSubscribedDocument]
		user: DF.Link | None
	# end: auto-generated types

	def on_update(self):
		from creqit.desk.notifications import clear_notification_config

		clear_notification_config(creqit.session.user)


def is_notifications_enabled(user):
	enabled = creqit.db.get_value("Notification Settings", user, "enabled")
	if enabled is None:
		return True
	return enabled


def is_email_notifications_enabled(user):
	enabled = creqit.db.get_value("Notification Settings", user, "enable_email_notifications")
	if enabled is None:
		return True
	return enabled


def is_email_notifications_enabled_for_type(user, notification_type):
	if not is_email_notifications_enabled(user):
		return False

	if notification_type == "Alert":
		return False

	fieldname = "enable_email_" + creqit.scrub(notification_type)
	enabled = creqit.db.get_value("Notification Settings", user, fieldname, ignore=True)
	if enabled is None:
		return True

	return enabled


def create_notification_settings(user):
	if not creqit.db.exists("Notification Settings", user):
		_doc = creqit.new_doc("Notification Settings")
		_doc.name = user
		_doc.insert(ignore_permissions=True)


def toggle_notifications(user: str, enable: bool = False, ignore_permissions=False):
	try:
		settings = creqit.get_doc("Notification Settings", user)
	except creqit.DoesNotExistError:
		creqit.clear_last_message()
		return

	if settings.enabled != enable:
		settings.enabled = enable
		settings.save(ignore_permissions=ignore_permissions)


@creqit.whitelist()
def get_subscribed_documents():
	if not creqit.session.user:
		return []

	try:
		if creqit.db.exists("Notification Settings", creqit.session.user):
			doc = creqit.get_doc("Notification Settings", creqit.session.user)
			return [item.document for item in doc.subscribed_documents]
	# Notification Settings is fetched even before sync doctype is called
	# but it will throw an ImportError, we can ignore it in migrate
	except ImportError:
		pass

	return []


def get_permission_query_conditions(user):
	if not user:
		user = creqit.session.user

	if user == "Administrator":
		return

	roles = creqit.get_roles(user)
	if "System Manager" in roles:
		return """(`tabNotification Settings`.name != 'Administrator')"""

	return f"""(`tabNotification Settings`.name = {creqit.db.escape(user)})"""


def has_permission(doc, ptype="read", user=None):
	# - Administrator can access everything.
	# - System managers can access everything except admin.
	# - Everyone else can only access their document.
	user = user or creqit.session.user

	if user == "Administrator":
		return True

	if "System Manager" in creqit.get_roles(user):
		return doc.name != "Administrator"

	return doc.name == user


@creqit.whitelist()
def set_seen_value(value, user):
	if creqit.flags.read_only:
		return

	creqit.db.set_value("Notification Settings", user, "seen", value, update_modified=False)
