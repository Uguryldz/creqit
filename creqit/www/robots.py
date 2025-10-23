import creqit

base_template_path = "www/robots.txt"


def get_context(context):
	robots_txt = (
		creqit.db.get_single_value("Website Settings", "robots_txt")
		or (creqit.local.conf.robots_txt and creqit.read_file(creqit.local.conf.robots_txt))
		or ""
	)

	return {"robots_txt": robots_txt}
