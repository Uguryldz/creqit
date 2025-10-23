import creqit


def execute():
	creqit.reload_doc("website", "doctype", "web_page_view", force=True)
	site_url = creqit.utils.get_site_url(creqit.local.site)
	creqit.db.sql(f"""UPDATE `tabWeb Page View` set is_unique=1 where referrer LIKE '%{site_url}%'""")
