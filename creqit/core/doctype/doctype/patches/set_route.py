import creqit
from creqit.desk.utils import slug


def execute():
	for doctype in creqit.get_all("DocType", ["name", "route"], dict(istable=0)):
		if not doctype.route:
			creqit.db.set_value("DocType", doctype.name, "route", slug(doctype.name), update_modified=False)
