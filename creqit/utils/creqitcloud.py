import creqit

creqit_CLOUD_DOMAINS = ("creqit.cloud", "creqit.com", "creqithr.com")


def on_creqitcloud() -> bool:
	"""Returns true if running on creqit Cloud.


	Useful for modifying few features for better UX."""
	return creqit.local.site.endswith(creqit_CLOUD_DOMAINS)
