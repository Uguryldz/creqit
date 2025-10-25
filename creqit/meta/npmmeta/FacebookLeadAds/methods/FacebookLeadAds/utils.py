# Copyright (c) 2025, creqit Technologies and contributors
# License: MIT. See LICENSE

"""
Facebook Lead Ads API Helper Functions
Based on Facebook Graph API v17.0+
"""

import requests
import creqit
from creqit import _


def get_settings():
	"""Get Facebook Lead Ads Settings"""
	return creqit.get_single("Facebook Lead Ads Settings")


def get_app_access_token():
	"""Get Facebook App Access Token"""
	settings = get_settings()
	
	if not settings.enabled:
		creqit.throw(_("Facebook Lead Ads is not enabled"))
	
	# Get app credentials
	app_id = settings.app_id
	app_secret = settings.get_password("app_secret")
	
	# Request app access token
	url = f"{settings.access_token_url}"
	params = {
		"client_id": app_id,
		"client_secret": app_secret,
		"grant_type": "client_credentials"
	}
	
	try:
		response = requests.post(url, data=params)
		response.raise_for_status()
		token_data = response.json()
		return token_data.get("access_token")
	except Exception as e:
		creqit.log_error("Facebook App Access Token Error")
		creqit.throw(_("Failed to get app access token: {0}").format(str(e)))


def facebook_api_request(endpoint, method="GET", params=None, data=None, use_app_token=False):
	"""
	Make a request to Facebook Graph API
	
	Args:
		endpoint: API endpoint (e.g., '/me/accounts')
		method: HTTP method (GET, POST, DELETE)
		params: Query parameters
		data: Request body data
		use_app_token: Use app access token instead of user token
	"""
	settings = get_settings()
	api_version = settings.api_version or "v17.0"
	base_url = f"https://graph.facebook.com/{api_version}"
	
	# Get access token
	if use_app_token:
		access_token = get_app_access_token()
	else:
		access_token = settings.get_access_token()
		if not access_token:
			creqit.throw(_("Please configure Facebook access token"))
	
	# Prepare request
	url = f"{base_url}{endpoint}"
	headers = {
		"Authorization": f"Bearer {access_token}",
		"Content-Type": "application/json"
	}
	
	if params is None:
		params = {}
	
	try:
		if method == "GET":
			response = requests.get(url, headers=headers, params=params)
		elif method == "POST":
			response = requests.post(url, headers=headers, params=params, json=data)
		elif method == "DELETE":
			response = requests.delete(url, headers=headers, params=params)
		else:
			creqit.throw(_("Unsupported HTTP method: {0}").format(method))
		
		response.raise_for_status()
		return response.json()
	except requests.exceptions.RequestException as e:
		creqit.log_error("Facebook API Request Error")
		error_msg = str(e)
		if hasattr(e.response, 'json'):
			try:
				error_data = e.response.json()
				error_msg = error_data.get('error', {}).get('message', error_msg)
			except:
				pass
		creqit.throw(_("Facebook API Error: {0}").format(error_msg))


def get_page_list(cursor=None):
	"""Get list of Facebook pages accessible by the user"""
	params = {
		"fields": "id,name,access_token",
	}
	
	if cursor:
		params["after"] = cursor
	
	response = facebook_api_request("/me/accounts", params=params)
	return response


def get_page_details(page_id, fields="id,name,access_token"):
	"""Get details of a specific Facebook page"""
	params = {"fields": fields}
	response = facebook_api_request(f"/{page_id}", params=params)
	return response


def get_form_list(page_id, cursor=None):
	"""Get list of lead forms for a specific page"""
	# Get page access token first
	page = get_page_details(page_id)
	page_access_token = page.get("access_token")
	
	if not page_access_token:
		creqit.throw(_("Could not get page access token"))
	
	# Use page access token to get forms
	params = {
		"fields": "id,name,status,locale",
		"access_token": page_access_token
	}
	
	if cursor:
		params["after"] = cursor
	
	settings = get_settings()
	api_version = settings.api_version or "v17.0"
	url = f"https://graph.facebook.com/{api_version}/{page_id}/leadgen_forms"
	
	try:
		response = requests.get(url, params=params)
		response.raise_for_status()
		return response.json()
	except Exception as e:
		creqit.log_error("Facebook Form List Error")
		creqit.throw(_("Failed to get form list: {0}").format(str(e)))


def get_lead_details(lead_id, fields="field_data,created_time,ad_id,ad_name,adset_id,adset_name,form_id"):
	"""Get details of a specific lead"""
	params = {"fields": fields}
	response = facebook_api_request(f"/{lead_id}", params=params)
	return response


def get_form_details(form_id, fields="id,name,locale,status,page,questions"):
	"""Get details of a specific form"""
	params = {"fields": fields}
	response = facebook_api_request(f"/{form_id}", params=params)
	return response


def list_app_webhook_subscriptions(app_id):
	"""List all webhook subscriptions for the app"""
	response = facebook_api_request(
		f"/{app_id}/subscriptions",
		use_app_token=True
	)
	return response.get("data", [])


def create_app_webhook_subscription(app_id, callback_url, verify_token, fields, include_values=True):
	"""
	Create a webhook subscription for the app
	
	Args:
		app_id: Facebook App ID
		callback_url: Webhook callback URL
		verify_token: Verification token
		fields: List of fields to subscribe to (e.g., ['leadgen'])
		include_values: Include field values in webhook payload
	"""
	data = {
		"object": "page",
		"callback_url": callback_url,
		"verify_token": verify_token,
		"fields": ",".join(fields) if isinstance(fields, list) else fields,
		"include_values": include_values
	}
	
	response = facebook_api_request(
		f"/{app_id}/subscriptions",
		method="POST",
		params=data,
		use_app_token=True
	)
	return response


def delete_app_webhook_subscription(app_id, object_type="page"):
	"""Delete a webhook subscription"""
	params = {"object": object_type}
	response = facebook_api_request(
		f"/{app_id}/subscriptions",
		method="DELETE",
		params=params,
		use_app_token=True
	)
	return response


def install_app_on_page(page_id, subscribed_fields="leadgen"):
	"""Install the app on a Facebook page"""
	# Get page access token
	page = get_page_details(page_id)
	page_access_token = page.get("access_token")
	
	if not page_access_token:
		creqit.throw(_("Could not get page access token"))
	
	settings = get_settings()
	api_version = settings.api_version or "v17.0"
	url = f"https://graph.facebook.com/{api_version}/{page_id}/subscribed_apps"
	
	params = {
		"subscribed_fields": subscribed_fields,
		"access_token": page_access_token
	}
	
	try:
		response = requests.post(url, params=params)
		response.raise_for_status()
		return response.json()
	except Exception as e:
		creqit.log_error("Facebook App Installation Error")
		creqit.throw(_("Failed to install app on page: {0}").format(str(e)))


def simplify_lead_data(lead, form):
	"""
	Simplify lead data for easier consumption
	
	Args:
		lead: Lead data from Facebook
		form: Form data from Facebook
	
	Returns:
		Simplified lead data
	"""
	simplified = {
		"id": lead.get("id"),
		"data": {},
		"form": {
			"id": form.get("id"),
			"name": form.get("name"),
			"locale": form.get("locale"),
			"status": form.get("status")
		},
		"created_time": lead.get("created_time")
	}
	
	# Add ad information if available
	if lead.get("ad_id"):
		simplified["ad"] = {
			"id": lead.get("ad_id"),
			"name": lead.get("ad_name")
		}
	
	if lead.get("adset_id"):
		simplified["adset"] = {
			"id": lead.get("adset_id"),
			"name": lead.get("adset_name")
		}
	
	# Add page information
	if form.get("page"):
		simplified["page"] = form.get("page")
	
	# Simplify field data
	for field in lead.get("field_data", []):
		field_name = field.get("name")
		field_values = field.get("values", [])
		simplified["data"][field_name] = field_values[0] if field_values else None
	
	return simplified

