import creqit
import creqit.share


def execute():
	for user in creqit.STANDARD_USERS:
		creqit.share.remove("User", user, user)
