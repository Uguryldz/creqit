import json
from urllib.parse import quote, urlencode

from oauthlib.oauth2 import FatalClientError, OAuth2Error
from oauthlib.openid.connect.core.endpoints.pre_configured import Server as WebApplicationServer

import creqit
from creqit.integrations.doctype.oauth_provider_settings.oauth_provider_settings import (
	get_oauth_settings,
)
from creqit.oauth import (
	OAuthWebRequestValidator,
	generate_json_error_response,
	get_server_url,
	get_userinfo,
)


def get_oauth_server():
	if not getattr(creqit.local, "oauth_server", None):
		oauth_validator = OAuthWebRequestValidator()
		creqit.local.oauth_server = WebApplicationServer(oauth_validator)

	return creqit.local.oauth_server


def sanitize_kwargs(param_kwargs):
	"""Remove 'data' and 'cmd' keys, if present."""
	arguments = param_kwargs
	arguments.pop("data", None)
	arguments.pop("cmd", None)

	return arguments


def encode_params(params):
	"""
	Encode a dict of params into a query string.

	Use `quote_via=urllib.parse.quote` so that whitespaces will be encoded as
	`%20` instead of as `+`. This is needed because oauthlib cannot handle `+`
	as a whitespace.
	"""
	return urlencode(params, quote_via=quote)


@creqit.whitelist()
def approve(*args, **kwargs):
	r = creqit.request

	try:
		(
			scopes,
			creqit.flags.oauth_credentials,
		) = get_oauth_server().validate_authorization_request(r.url, r.method, r.get_data(), r.headers)

		headers, body, status = get_oauth_server().create_authorization_response(
			uri=creqit.flags.oauth_credentials["redirect_uri"],
			body=r.get_data(),
			headers=r.headers,
			scopes=scopes,
			credentials=creqit.flags.oauth_credentials,
		)
		uri = headers.get("Location", None)

		creqit.local.response["type"] = "redirect"
		creqit.local.response["location"] = uri
		return

	except (FatalClientError, OAuth2Error) as e:
		return generate_json_error_response(e)


@creqit.whitelist(allow_guest=True)
def authorize(**kwargs):
	success_url = "/api/method/creqit.integrations.oauth2.approve?" + encode_params(sanitize_kwargs(kwargs))
	failure_url = creqit.form_dict["redirect_uri"] + "?error=access_denied"

	if creqit.session.user == "Guest":
		# Force login, redirect to preauth again.
		creqit.local.response["type"] = "redirect"
		creqit.local.response["location"] = "/login?" + encode_params({"redirect-to": creqit.request.url})
	else:
		try:
			r = creqit.request
			(
				scopes,
				creqit.flags.oauth_credentials,
			) = get_oauth_server().validate_authorization_request(r.url, r.method, r.get_data(), r.headers)

			skip_auth = creqit.db.get_value(
				"OAuth Client",
				creqit.flags.oauth_credentials["client_id"],
				"skip_authorization",
			)
			unrevoked_tokens = creqit.get_all("OAuth Bearer Token", filters={"status": "Active"})

			if skip_auth or (get_oauth_settings().skip_authorization == "Auto" and unrevoked_tokens):
				creqit.local.response["type"] = "redirect"
				creqit.local.response["location"] = success_url
			else:
				if "openid" in scopes:
					scopes.remove("openid")
					scopes.extend(["Full Name", "Email", "User Image", "Roles"])

				# Show Allow/Deny screen.
				response_html_params = creqit._dict(
					{
						"client_id": creqit.db.get_value("OAuth Client", kwargs["client_id"], "app_name"),
						"success_url": success_url,
						"failure_url": failure_url,
						"details": scopes,
					}
				)
				resp_html = creqit.render_template(
					"templates/includes/oauth_confirmation.html", response_html_params
				)
				creqit.respond_as_web_page("Confirm Access", resp_html, primary_action=None)
		except (FatalClientError, OAuth2Error) as e:
			return generate_json_error_response(e)


@creqit.whitelist(allow_guest=True)
def get_token(*args, **kwargs):
	try:
		r = creqit.request
		headers, body, status = get_oauth_server().create_token_response(
			r.url, r.method, r.form, r.headers, creqit.flags.oauth_credentials
		)
		body = creqit._dict(json.loads(body))

		if body.error:
			creqit.local.response = body
			creqit.local.response["http_status_code"] = 400
			return

		creqit.local.response = body
		return

	except (FatalClientError, OAuth2Error) as e:
		return generate_json_error_response(e)


@creqit.whitelist(allow_guest=True)
def revoke_token(*args, **kwargs):
	try:
		r = creqit.request
		headers, body, status = get_oauth_server().create_revocation_response(
			r.url,
			headers=r.headers,
			body=r.form,
			http_method=r.method,
		)
	except (FatalClientError, OAuth2Error):
		pass

	# status_code must be 200
	creqit.local.response = creqit._dict({})
	creqit.local.response["http_status_code"] = status or 200
	return


@creqit.whitelist()
def openid_profile(*args, **kwargs):
	try:
		r = creqit.request
		headers, body, status = get_oauth_server().create_userinfo_response(
			r.url,
			headers=r.headers,
			body=r.form,
		)
		body = creqit._dict(json.loads(body))
		creqit.local.response = body
		return

	except (FatalClientError, OAuth2Error) as e:
		return generate_json_error_response(e)


@creqit.whitelist(allow_guest=True)
def openid_configuration():
	creqit_server_url = get_server_url()
	creqit.local.response = creqit._dict(
		{
			"issuer": creqit_server_url,
			"authorization_endpoint": f"{creqit_server_url}/api/method/creqit.integrations.oauth2.authorize",
			"token_endpoint": f"{creqit_server_url}/api/method/creqit.integrations.oauth2.get_token",
			"userinfo_endpoint": f"{creqit_server_url}/api/method/creqit.integrations.oauth2.openid_profile",
			"revocation_endpoint": f"{creqit_server_url}/api/method/creqit.integrations.oauth2.revoke_token",
			"introspection_endpoint": f"{creqit_server_url}/api/method/creqit.integrations.oauth2.introspect_token",
			"response_types_supported": [
				"code",
				"token",
				"code id_token",
				"code token id_token",
				"id_token",
				"id_token token",
			],
			"subject_types_supported": ["public"],
			"id_token_signing_alg_values_supported": ["HS256"],
		}
	)


@creqit.whitelist(allow_guest=True)
def introspect_token(token=None, token_type_hint=None):
	if token_type_hint not in ["access_token", "refresh_token"]:
		token_type_hint = "access_token"
	try:
		bearer_token = None
		if token_type_hint == "access_token":
			bearer_token = creqit.get_doc("OAuth Bearer Token", {"access_token": token})
		elif token_type_hint == "refresh_token":
			bearer_token = creqit.get_doc("OAuth Bearer Token", {"refresh_token": token})

		client = creqit.get_doc("OAuth Client", bearer_token.client)

		token_response = creqit._dict(
			{
				"client_id": client.client_id,
				"trusted_client": client.skip_authorization,
				"active": bearer_token.status == "Active",
				"exp": round(bearer_token.expiration_time.timestamp()),
				"scope": bearer_token.scopes,
			}
		)

		if "openid" in bearer_token.scopes:
			sub = creqit.get_value(
				"User Social Login",
				{"provider": "creqit", "parent": bearer_token.user},
				"userid",
			)

			if sub:
				token_response.update({"sub": sub})
				user = creqit.get_doc("User", bearer_token.user)
				userinfo = get_userinfo(user)
				token_response.update(userinfo)

		creqit.local.response = token_response

	except Exception:
		creqit.local.response = creqit._dict({"active": False})
