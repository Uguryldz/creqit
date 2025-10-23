import creqit
from creqit.desk.doctype.notification_settings.notification_settings import (
	create_notification_settings,
)


def execute():
	creqit.reload_doc("desk", "doctype", "notification_settings")
	creqit.reload_doc("desk", "doctype", "notification_subscribed_document")

	users = creqit.get_all("User", fields=["name"])
	for user in users:
		create_notification_settings(user.name)
