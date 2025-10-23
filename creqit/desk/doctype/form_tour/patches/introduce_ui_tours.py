import json

import creqit


def execute():
	"""Handle introduction of UI tours"""
	completed = {}
	for tour in creqit.get_all("Form Tour", {"ui_tour": 1}, pluck="name"):
		completed[tour] = {"is_complete": True}

	User = creqit.qb.DocType("User")
	creqit.qb.update(User).set("onboarding_status", json.dumps(completed)).run()
