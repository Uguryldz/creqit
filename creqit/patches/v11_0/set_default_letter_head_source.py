import creqit


def execute():
	creqit.reload_doctype("Letter Head")

	# source of all existing letter heads must be HTML
	creqit.db.sql("update `tabLetter Head` set source = 'HTML'")
