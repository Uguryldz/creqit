import creqit
from creqit.cache_manager import clear_defaults_cache


def execute():
	creqit.db.set_default(
		"suspend_email_queue",
		creqit.db.get_default("hold_queue", "Administrator") or 0,
		parent="__default",
	)

	creqit.db.delete("DefaultValue", {"defkey": "hold_queue"})
	clear_defaults_cache()
