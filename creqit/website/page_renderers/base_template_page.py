import creqit
from creqit.website.doctype.website_settings.website_settings import get_website_settings
from creqit.website.page_renderers.base_renderer import BaseRenderer
from creqit.website.website_components.metatags import MetaTags


class BaseTemplatePage(BaseRenderer):
	def __init__(self, path, http_status_code=None):
		super().__init__(path=path, http_status_code=http_status_code)
		self.template_path = ""
		self.source = ""

	def init_context(self):
		self.context = creqit._dict()
		self.context.update(get_website_settings())
		self.context.update(creqit.local.conf.get("website_context") or {})

	def add_csrf_token(self, html):
		if creqit.local.session:
			csrf_token = creqit.local.session.data.csrf_token
			return html.replace(
				"<!-- csrf_token -->", f'<script>creqit.csrf_token = "{csrf_token}";</script>'
			)

		return html

	def post_process_context(self):
		self.tags = MetaTags(self.path, self.context).tags
		self.context.metatags = self.tags
		self.set_base_template_if_missing()
		self.set_title_with_prefix()
		self.update_website_context()
		# context sends us a new template path
		self.template_path = self.context.template or self.template_path
		self.context._context_dict = self.context
		self.set_missing_values()

	def set_base_template_if_missing(self):
		if not self.context.base_template_path:
			app_base = creqit.get_hooks("base_template")
			self.context.base_template_path = app_base[-1] if app_base else "templates/base.html"

	def set_title_with_prefix(self):
		if (
			self.context.title_prefix
			and self.context.title
			and not self.context.title.startswith(self.context.title_prefix)
		):
			self.context.title = f"{self.context.title_prefix} - {self.context.title}"

	def set_missing_values(self):
		# set using creqit.respond_as_web_page
		if hasattr(creqit.local, "response") and creqit.local.response.get("context"):
			self.context.update(creqit.local.response.context)

		# to be able to inspect the context dict
		# Use the macro "inspect" from macros.html
		self.context.canonical = creqit.utils.get_url(creqit.utils.escape_html(self.path))

		if "url_prefix" not in self.context:
			self.context.url_prefix = ""

		if self.context.url_prefix and self.context.url_prefix[-1] != "/":
			self.context.url_prefix += "/"

		self.context.path = self.path
		self.context.pathname = getattr(creqit.local, "path", None) if hasattr(creqit, "local") else self.path

	def update_website_context(self):
		# apply context from hooks
		update_website_context = creqit.get_hooks("update_website_context")
		for method in update_website_context:
			values = creqit.get_attr(method)(self.context)
			if values:
				self.context.update(values)
