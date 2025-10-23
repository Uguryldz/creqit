import creqit
from creqit.website.page_renderers.template_page import TemplatePage


class ListPage(TemplatePage):
	def can_render(self):
		return creqit.db.exists("DocType", self.path, True)

	def render(self):
		creqit.local.form_dict.doctype = self.path
		self.set_standard_path("list")
		return super().render()
