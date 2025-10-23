import creqit
from creqit import _
from creqit.utils import cstr
from creqit.website.page_renderers.template_page import TemplatePage


class NotPermittedPage(TemplatePage):
	def __init__(self, path=None, http_status_code=None, exception=""):
		creqit.local.message = cstr(exception)
		super().__init__(path=path, http_status_code=http_status_code)
		self.http_status_code = 403

	def can_render(self):
		return True

	def render(self):
		action = f"/login?redirect-to={creqit.request.path}"
		if creqit.request.path.startswith("/app/") or creqit.request.path == "/app":
			action = "/login"
		creqit.local.message_title = _("Not Permitted")
		creqit.local.response["context"] = dict(
			indicator_color="red", primary_action=action, primary_label=_("Login"), fullpage=True
		)
		self.set_standard_path("message")
		return super().render()
