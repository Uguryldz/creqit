import creqit
from creqit.utils.install import create_user_type


def execute():
	creqit.reload_doc("core", "doctype", "role")
	creqit.reload_doc("core", "doctype", "user_document_type")
	creqit.reload_doc("core", "doctype", "user_type_module")
	creqit.reload_doc("core", "doctype", "user_select_document_type")
	creqit.reload_doc("core", "doctype", "user_type")

	create_user_type()
