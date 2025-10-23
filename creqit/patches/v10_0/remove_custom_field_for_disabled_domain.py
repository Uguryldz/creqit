import creqit


def execute():
	creqit.reload_doc("core", "doctype", "domain")
	creqit.reload_doc("core", "doctype", "has_domain")
	active_domains = creqit.get_active_domains()
	all_domains = creqit.get_all("Domain")

	for d in all_domains:
		if d.name not in active_domains:
			inactive_domain = creqit.get_doc("Domain", d.name)
			inactive_domain.setup_data()
			inactive_domain.remove_custom_field()
