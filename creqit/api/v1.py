import json

from werkzeug.routing import Rule

import creqit
from creqit import _
from creqit.utils.data import sbool


def document_list(doctype: str):
	if creqit.form_dict.get("fields"):
		creqit.form_dict["fields"] = json.loads(creqit.form_dict["fields"])

	# set limit of records for creqit.get_list
	creqit.form_dict.setdefault(
		"limit_page_length",
		creqit.form_dict.limit or creqit.form_dict.limit_page_length or 20,
	)

	# convert strings to native types - only as_dict and debug accept bool
	for param in ["as_dict", "debug"]:
		param_val = creqit.form_dict.get(param)
		if param_val is not None:
			creqit.form_dict[param] = sbool(param_val)

	# evaluate creqit.get_list
	return creqit.call(creqit.client.get_list, doctype, **creqit.form_dict)


def handle_rpc_call(method: str):
	import creqit.handler

	method = method.split("/")[0]  # for backward compatiblity

	creqit.form_dict.cmd = method
	return creqit.handler.handle()


def create_doc(doctype: str):
	data = get_request_form_data()
	data.pop("doctype", None)
	return creqit.new_doc(doctype, **data).insert()


def update_doc(doctype: str, name: str):
	data = get_request_form_data()

	doc = creqit.get_doc(doctype, name, for_update=True)
	if "flags" in data:
		del data["flags"]

	doc.update(data)
	doc.save()

	# check for child table doctype
	if doc.get("parenttype"):
		creqit.get_doc(doc.parenttype, doc.parent).save()

	return doc


def delete_doc(doctype: str, name: str):
	# TODO: child doc handling
	creqit.delete_doc(doctype, name, ignore_missing=False)
	creqit.response.http_status_code = 202
	return "ok"


def read_doc(doctype: str, name: str):
	# Backward compatiblity
	if "run_method" in creqit.form_dict:
		return execute_doc_method(doctype, name)

	doc = creqit.get_doc(doctype, name)
	if not doc.has_permission("read"):
		raise creqit.PermissionError
	doc.apply_fieldlevel_read_permissions()
	return doc


def execute_doc_method(doctype: str, name: str, method: str | None = None):
	method = method or creqit.form_dict.pop("run_method")
	doc = creqit.get_doc(doctype, name)
	doc.is_whitelisted(method)

	if creqit.request.method == "GET":
		if not doc.has_permission("read"):
			creqit.throw(_("Not permitted"), creqit.PermissionError)
		return doc.run_method(method, **creqit.form_dict)

	elif creqit.request.method == "POST":
		if not doc.has_permission("write"):
			creqit.throw(_("Not permitted"), creqit.PermissionError)

		return doc.run_method(method, **creqit.form_dict)


def get_request_form_data():
	if creqit.form_dict.data is None:
		data = creqit.safe_decode(creqit.request.get_data())
	else:
		data = creqit.form_dict.data

	try:
		return creqit.parse_json(data)
	except ValueError:
		return creqit.form_dict


url_rules = [
	Rule("/method/<path:method>", endpoint=handle_rpc_call),
	Rule("/resource/<doctype>", methods=["GET"], endpoint=document_list),
	Rule("/resource/<doctype>", methods=["POST"], endpoint=create_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["GET"], endpoint=read_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["PUT"], endpoint=update_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["DELETE"], endpoint=delete_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["POST"], endpoint=execute_doc_method),
]
