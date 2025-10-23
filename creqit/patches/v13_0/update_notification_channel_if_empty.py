# Copyright (c) 2020, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	creqit.reload_doc("Email", "doctype", "Notification")

	notifications = creqit.get_all("Notification", {"is_standard": 1}, {"name", "channel"})
	for notification in notifications:
		if not notification.channel:
			creqit.db.set_value("Notification", notification.name, "channel", "Email", update_modified=False)
			creqit.db.commit()
