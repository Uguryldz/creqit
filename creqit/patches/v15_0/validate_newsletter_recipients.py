import creqit
from creqit.utils import validate_email_address


def execute():
	for name, email in creqit.get_all("Email Group Member", fields=["name", "email"], as_list=True):
		if not validate_email_address(email, throw=False):
			creqit.db.set_value("Email Group Member", name, "unsubscribed", 1)
			creqit.db.commit()
