import creqit


def execute():
	creqit.db.delete("DocType", {"name": "Feedback Request"})
