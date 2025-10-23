import creqit


def execute():
	creqit.reload_doc("core", "doctype", "user")
	creqit.db.sql(
		"""
		UPDATE `tabUser`
		SET `home_settings` = ''
		WHERE `user_type` = 'System User'
	"""
	)
