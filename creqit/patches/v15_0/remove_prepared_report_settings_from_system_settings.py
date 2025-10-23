import creqit
from creqit.utils import cint


def execute():
	expiry_period = (
		cint(creqit.db.get_singles_dict("System Settings").get("prepared_report_expiry_period")) or 30
	)
	creqit.get_single("Log Settings").register_doctype("Prepared Report", expiry_period)
