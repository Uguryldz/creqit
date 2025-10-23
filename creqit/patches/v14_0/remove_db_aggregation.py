import re

import creqit
from creqit.query_builder import DocType


def execute():
	"""Replace temporarily available Database Aggregate APIs on creqit (develop)

	APIs changed:
	        * creqit.db.max => creqit.qb.max
	        * creqit.db.min => creqit.qb.min
	        * creqit.db.sum => creqit.qb.sum
	        * creqit.db.avg => creqit.qb.avg
	"""
	ServerScript = DocType("Server Script")
	server_scripts = (
		creqit.qb.from_(ServerScript)
		.where(
			ServerScript.script.like("%creqit.db.max(%")
			| ServerScript.script.like("%creqit.db.min(%")
			| ServerScript.script.like("%creqit.db.sum(%")
			| ServerScript.script.like("%creqit.db.avg(%")
		)
		.select("name", "script")
		.run(as_dict=True)
	)

	for server_script in server_scripts:
		name, script = server_script["name"], server_script["script"]

		for agg in ["avg", "max", "min", "sum"]:
			script = re.sub(f"creqit.db.{agg}\\(", f"creqit.qb.{agg}(", script)

		creqit.db.set_value("Server Script", name, "script", script)
