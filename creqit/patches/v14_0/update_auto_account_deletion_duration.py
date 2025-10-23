import creqit


def execute():
	days = creqit.db.get_single_value("Website Settings", "auto_account_deletion")
	creqit.db.set_single_value("Website Settings", "auto_account_deletion", days * 24)
