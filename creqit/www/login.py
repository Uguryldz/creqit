# Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE


from urllib.parse import urlparse

import creqit
import creqit.utils
from creqit import _
from creqit.apps import get_default_path
from creqit.auth import LoginManager
from creqit.core.doctype.navbar_settings.navbar_settings import get_app_logo
from creqit.rate_limiter import rate_limit
from creqit.utils import cint, get_url
from creqit.utils.data import escape_html
from creqit.utils.html_utils import get_icon_html
from creqit.utils.jinja import guess_is_path
from creqit.utils.oauth import get_oauth2_authorize_url, get_oauth_keys, redirect_post_login
from creqit.utils.password import get_decrypted_password
from creqit.website.utils import get_home_page

no_cache = True


def get_context(context):
	redirect_to = creqit.local.request.args.get("redirect-to")
	redirect_to = sanitize_redirect(redirect_to)

	if creqit.session.user != "Guest":
		if not redirect_to:
			if creqit.session.data.user_type == "Website User":
				redirect_to = get_default_path() or get_home_page()
			else:
				redirect_to = get_default_path() or "/app"

		if redirect_to != "login":
			creqit.local.flags.redirect_location = redirect_to
			raise creqit.Redirect

	context.no_header = True
	context.for_test = "login.html"
	context["title"] = "Login"
	context["hide_login"] = True  # dont show login link on login page again.
	context["provider_logins"] = []
	context["disable_signup"] = cint(creqit.get_website_settings("disable_signup"))
	context["show_footer_on_login"] = cint(creqit.get_website_settings("show_footer_on_login"))
	context["disable_user_pass_login"] = cint(creqit.get_system_settings("disable_user_pass_login"))
	context["logo"] = get_app_logo()
	context["app_name"] = (
		creqit.get_website_settings("app_name") or creqit.get_system_settings("app_name") or _("creqit")
	)

	signup_form_template = creqit.get_hooks("signup_form_template")
	if signup_form_template and len(signup_form_template):
		path = signup_form_template[-1]
		if not guess_is_path(path):
			path = creqit.get_attr(signup_form_template[-1])()
	else:
		path = "creqit/templates/signup.html"

	if path:
		context["signup_form_template"] = creqit.get_template(path).render()

	providers = creqit.get_all(
		"Social Login Key",
		filters={"enable_social_login": 1},
		fields=["name", "client_id", "base_url", "provider_name", "icon"],
		order_by="name",
	)

	for provider in providers:
		client_secret = get_decrypted_password("Social Login Key", provider.name, "client_secret")
		if not client_secret:
			continue

		icon = None
		if provider.icon:
			if provider.provider_name == "Custom":
				icon = get_icon_html(provider.icon, small=True)
			else:
				icon = f"<img src={escape_html(provider.icon)!r} alt={escape_html(provider.provider_name)!r}>"

		if provider.client_id and provider.base_url and get_oauth_keys(provider.name):
			context.provider_logins.append(
				{
					"name": provider.name,
					"provider_name": provider.provider_name,
					"auth_url": get_oauth2_authorize_url(provider.name, redirect_to),
					"icon": icon,
				}
			)
			context["social_login"] = True

	if cint(creqit.db.get_value("LDAP Settings", "LDAP Settings", "enabled")):
		from creqit.integrations.doctype.ldap_settings.ldap_settings import LDAPSettings

		context["ldap_settings"] = LDAPSettings.get_ldap_client_settings()

	login_label = [_("Email")]

	if creqit.utils.cint(creqit.get_system_settings("allow_login_using_mobile_number")):
		login_label.append(_("Mobile"))

	if creqit.utils.cint(creqit.get_system_settings("allow_login_using_user_name")):
		login_label.append(_("Username"))

	context["login_label"] = f" {_('or')} ".join(login_label)

	context["login_with_email_link"] = creqit.get_system_settings("login_with_email_link")

	return context


@creqit.whitelist(allow_guest=True)
def login_via_token(login_token: str):
	sid = creqit.cache.get_value(f"login_token:{login_token}", expires=True)
	if not sid:
		creqit.respond_as_web_page(_("Invalid Request"), _("Invalid Login Token"), http_status_code=417)
		return

	creqit.local.form_dict.sid = sid
	creqit.local.login_manager = LoginManager()

	redirect_post_login(
		desk_user=creqit.db.get_value("User", creqit.session.user, "user_type") == "System User"
	)


@creqit.whitelist(allow_guest=True)
@rate_limit(limit=5, seconds=60 * 60)
def send_login_link(email: str):
	if not creqit.get_system_settings("login_with_email_link"):
		return

	expiry = creqit.get_system_settings("login_with_email_link_expiry") or 10
	link = _generate_temporary_login_link(email, expiry)

	app_name = (
		creqit.get_website_settings("app_name") or creqit.get_system_settings("app_name") or _("Creqit")
	)

	subject = _("Login To {0}").format(app_name)

	creqit.sendmail(
		subject=subject,
		recipients=email,
		template="login_with_email_link",
		args={"link": link, "minutes": expiry, "app_name": app_name},
		now=True,
	)


def _generate_temporary_login_link(email: str, expiry: int):
	assert isinstance(email, str)

	if not creqit.db.exists("User", email):
		creqit.throw(_("User with email address {0} does not exist").format(email), creqit.DoesNotExistError)
	key = creqit.generate_hash()
	creqit.cache.set_value(f"one_time_login_key:{key}", email, expires_in_sec=expiry * 60)

	return get_url(f"/api/method/creqit.www.login.login_via_key?key={key}")


def get_login_with_email_link_ratelimit() -> int:
	return creqit.get_system_settings("rate_limit_email_link_login") or 5


@creqit.whitelist(allow_guest=True, methods=["GET"])
@rate_limit(limit=get_login_with_email_link_ratelimit, seconds=60 * 60)
def login_via_key(key: str):
	cache_key = f"one_time_login_key:{key}"
	email = creqit.cache.get_value(cache_key)

	if email:
		creqit.cache.delete_value(cache_key)
		creqit.local.login_manager.login_as(email)

		redirect_post_login(
			desk_user=creqit.db.get_value("User", creqit.session.user, "user_type") == "System User"
		)
	else:
		creqit.respond_as_web_page(
			_("Not Permitted"),
			_("The link you trying to login is invalid or expired."),
			http_status_code=403,
			indicator_color="red",
		)


def sanitize_redirect(redirect: str | None) -> str | None:
	"""Only allow redirect on same domain.

	Allowed redirects:
	- Same host e.g. https://creqit.localhost/path
	- Just path e.g. /app
	"""
	if not redirect:
		return redirect

	parsed_redirect = urlparse(redirect)
	if not parsed_redirect.netloc:
		return redirect

	parsed_request_host = urlparse(creqit.local.request.url)
	if parsed_request_host.netloc == parsed_redirect.netloc:
		return redirect

	return None
