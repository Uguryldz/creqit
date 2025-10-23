import creqit


def execute():
	creqit.delete_doc_if_exists("DocType", "Web View")
	creqit.delete_doc_if_exists("DocType", "Web View Component")
	creqit.delete_doc_if_exists("DocType", "CSS Class")
