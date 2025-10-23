import creqit
from creqit.utils import cint


def execute():
	creqit.reload_doctype("Dropbox Settings")
	check_dropbox_enabled = cint(creqit.db.get_single_value("Dropbox Settings", "enabled"))
	if check_dropbox_enabled == 1:
		creqit.db.set_single_value("Dropbox Settings", "file_backup", 1)
