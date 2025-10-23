import creqit


def execute():
	"""
	Deprecate Feedback Trigger and Rating. This feature was not customizable.
	Now can be achieved via custom Web Forms
	"""
	creqit.delete_doc("DocType", "Feedback Trigger")
	creqit.delete_doc("DocType", "Feedback Rating")
