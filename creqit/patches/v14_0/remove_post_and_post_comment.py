import creqit


def execute():
	creqit.delete_doc_if_exists("DocType", "Post")
	creqit.delete_doc_if_exists("DocType", "Post Comment")
