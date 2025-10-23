import json

import creqit


def execute():
	if creqit.db.exists("Social Login Key", "github"):
		creqit.db.set_value(
			"Social Login Key", "github", "auth_url_data", json.dumps({"scope": "user:email"})
		)
