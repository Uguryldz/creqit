import creqit


def execute():
	creqit.reload_doc("website", "doctype", "web_page_view", force=True)
	creqit.db.sql("""UPDATE `tabWeb Page View` set path='/' where path=''""")
