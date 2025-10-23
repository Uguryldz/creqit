# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit
from creqit.utils import strip_html_tags
from creqit.utils.html_utils import clean_html

no_cache = 1


def get_context(context):
	message_context = creqit._dict()
	if hasattr(creqit.local, "message"):
		message_context["header"] = creqit.local.message_title
		message_context["title"] = strip_html_tags(creqit.local.message_title)
		message_context["message"] = creqit.local.message
		if hasattr(creqit.local, "message_success"):
			message_context["success"] = creqit.local.message_success

	elif creqit.local.form_dict.id:
		message_id = creqit.local.form_dict.id
		key = f"message_id:{message_id}"
		message = creqit.cache.get_value(key, expires=True)
		if message:
			message_context.update(message.get("context", {}))
			if message.get("http_status_code"):
				creqit.local.response["http_status_code"] = message["http_status_code"]

	if not message_context.title:
		message_context.title = clean_html(creqit.form_dict.title)

	if not message_context.message:
		message_context.message = clean_html(creqit.form_dict.message)

	return message_context
