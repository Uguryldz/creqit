# Copyright (c) 2025, creqit Technologies and contributors
# License: MIT. See LICENSE

"""
Facebook Lead Ads Webhook Handler
Handles incoming webhook requests from Facebook
"""

import hashlib
import hmac
import json

import creqit
from creqit import _
from creqit.meta.FacebookLeadAds.utils import (
	get_lead_details,
	get_form_details,
	simplify_lead_data,
	get_settings
)


@creqit.whitelist(allow_guest=True)
def handle_webhook():
	"""
	Main webhook handler for Facebook Lead Ads
	Handles both GET (verification) and POST (lead data) requests
	"""
	try:
		if creqit.request.method == "GET":
			return handle_verification()
		elif creqit.request.method == "POST":
			return handle_lead_event()
		else:
			creqit.throw(_("Unsupported HTTP method"))
	except Exception as e:
		creqit.log_error("Facebook Webhook Error")
		creqit.response.status_code = 500
		return {"error": str(e)}


def handle_verification():
	"""
	Handle Facebook webhook verification (GET request)
	Facebook sends a verification request when setting up the webhook
	"""
	# Get query parameters
	mode = creqit.request.args.get("hub.mode")
	token = creqit.request.args.get("hub.verify_token")
	challenge = creqit.request.args.get("hub.challenge")
	
	# Find webhook with matching verify token
	webhooks = creqit.get_all(
		"Facebook Lead Ads Webhook",
		filters={"verify_token": token, "enabled": 1},
		limit=1
	)
	
	if not webhooks:
		creqit.log_error("Invalid verify token")
		creqit.response.status_code = 403
		return {"error": "Invalid verify token"}
	
	if mode == "subscribe":
		# Return the challenge to verify the webhook
		return challenge
	
	creqit.response.status_code = 403
	return {"error": "Invalid mode"}


def handle_lead_event():
	"""
	Handle incoming lead event from Facebook (POST request)
	"""
	try:
		# Verify request signature
		if not verify_signature():
			creqit.log_error("Invalid signature")
			creqit.response.status_code = 403
			return {"error": "Invalid signature"}
		
		# Parse webhook payload
		payload = creqit.request.get_json()
		
		if not payload:
			creqit.response.status_code = 400
			return {"error": "Invalid payload"}
		
		# Check if it's a page event
		if payload.get("object") != "page":
			creqit.response.status_code = 200
			return {"success": True}
		
		# Process each entry
		for entry in payload.get("entry", []):
			process_entry(entry)
		
		# Return success response
		creqit.response.status_code = 200
		return {"success": True}
		
	except Exception as e:
		creqit.log_error("Facebook Lead Event Processing Error")
		creqit.response.status_code = 500
		return {"error": str(e)}


def verify_signature():
	"""
	Verify that the request is from Facebook
	Uses HMAC SHA-256 signature verification
	"""
	try:
		# Get signature from headers
		signature = creqit.request.headers.get("X-Hub-Signature-256", "")
		
		if not signature:
			return False
		
		# Get app secret
		settings = get_settings()
		app_secret = settings.get_password("app_secret")
		
		if not app_secret:
			return False
		
		# Get request body
		body = creqit.request.get_data()
		
		# Calculate expected signature
		expected_signature = "sha256=" + hmac.new(
			app_secret.encode("utf-8"),
			body,
			hashlib.sha256
		).hexdigest()
		
		# Compare signatures
		return hmac.compare_digest(signature, expected_signature)
		
	except Exception as e:
		creqit.log_error("Signature Verification Error")
		return False


def process_entry(entry):
	"""
	Process a single webhook entry
	
	Args:
		entry: Webhook entry data from Facebook
	"""
	entry_id = entry.get("id")
	changes = entry.get("changes", [])
	
	for change in changes:
		# Check if it's a leadgen event
		if change.get("field") != "leadgen":
			continue
		
		value = change.get("value", {})
		page_id = value.get("page_id")
		form_id = value.get("form_id")
		leadgen_id = value.get("leadgen_id")
		
		# Find matching webhook
		webhooks = creqit.get_all(
			"Facebook Lead Ads Webhook",
			filters={
				"page_id": page_id,
				"form_id": form_id,
				"enabled": 1
			},
			limit=1
		)
		
		if not webhooks:
			creqit.log_error(f"No webhook found for page {page_id} and form {form_id}")
			continue
		
		webhook = creqit.get_doc("Facebook Lead Ads Webhook", webhooks[0].name)
		
		# Fetch lead details from Facebook
		try:
			lead_data = get_lead_details(leadgen_id)
			form_data = get_form_details(form_id)
			
			# Process the lead
			if webhook.simplify_output:
				processed_data = simplify_lead_data(lead_data, form_data)
			else:
				processed_data = {
					"id": lead_data.get("id"),
					"field_data": lead_data.get("field_data"),
					"form": form_data,
					"ad": {
						"id": lead_data.get("ad_id"),
						"name": lead_data.get("ad_name")
					},
					"adset": {
						"id": lead_data.get("adset_id"),
						"name": lead_data.get("adset_name")
					},
					"page": form_data.get("page"),
					"created_time": lead_data.get("created_time"),
					"event": value
				}
			
			# Process the lead through webhook
			webhook.process_lead(processed_data)
			
			# Create a Lead document (if Lead DocType exists)
			create_lead_document(webhook, processed_data)
			
		except Exception as e:
			creqit.log_error(f"Error processing lead {leadgen_id}")
			creqit.log_error(str(e))


def create_lead_document(webhook, lead_data):
	"""
	Create a Lead document from Facebook lead data
	This is a placeholder - customize based on your Lead DocType structure
	
	Args:
		webhook: Facebook Lead Ads Webhook document
		lead_data: Processed lead data
	"""
	try:
		# Check if Lead DocType exists
		if not creqit.db.exists("DocType", "Lead"):
			return
		
		# Prepare lead document data
		lead_doc_data = {
			"doctype": "Lead",
			"source": "Facebook Lead Ads",
			"lead_name": lead_data.get("data", {}).get("full_name") or lead_data.get("data", {}).get("first_name", "Unknown"),
			"email_id": lead_data.get("data", {}).get("email"),
			"phone": lead_data.get("data", {}).get("phone_number"),
			"company_name": lead_data.get("data", {}).get("company_name"),
			# Add custom fields as needed
			"facebook_lead_id": lead_data.get("id"),
			"facebook_form_id": webhook.form_id,
			"facebook_page_id": webhook.page_id,
			"facebook_ad_id": lead_data.get("ad", {}).get("id"),
			"facebook_adset_id": lead_data.get("adset", {}).get("id"),
			"facebook_lead_data": json.dumps(lead_data, indent=2)
		}
		
		# Create the lead document
		lead_doc = creqit.get_doc(lead_doc_data)
		lead_doc.insert(ignore_permissions=True)
		creqit.db.commit()
		
		creqit.logger().info(f"Created Lead document {lead_doc.name} from Facebook Lead {lead_data.get('id')}")
		
	except Exception as e:
		creqit.log_error("Lead Document Creation Error")
		creqit.logger().error(f"Failed to create Lead document: {str(e)}")


@creqit.whitelist()
def test_webhook(webhook_name):
	"""
	Test webhook configuration
	
	Args:
		webhook_name: Name of the Facebook Lead Ads Webhook
	"""
	webhook = creqit.get_doc("Facebook Lead Ads Webhook", webhook_name)
	
	return {
		"webhook_url": webhook.webhook_url,
		"verify_token": webhook.verify_token,
		"is_active": webhook.is_active,
		"enabled": webhook.enabled
	}


@creqit.whitelist()
def get_page_list():
	"""Get list of available Facebook pages"""
	from creqit.meta.FacebookLeadAds.utils import get_page_list as fetch_pages
	
	try:
		result = fetch_pages()
		pages = result.get("data", [])
		
		return {
			"pages": [
				{
					"value": page.get("id"),
					"label": page.get("name")
				}
				for page in pages
			]
		}
	except Exception as e:
		creqit.throw(_("Failed to fetch pages: {0}").format(str(e)))


@creqit.whitelist()
def get_form_list(page_id):
	"""
	Get list of lead forms for a page
	
	Args:
		page_id: Facebook Page ID
	"""
	from creqit.meta.FacebookLeadAds.utils import get_form_list as fetch_forms
	
	try:
		result = fetch_forms(page_id)
		forms = result.get("data", [])
		
		return {
			"forms": [
				{
					"value": form.get("id"),
					"label": form.get("name")
				}
				for form in forms
			]
		}
	except Exception as e:
		creqit.throw(_("Failed to fetch forms: {0}").format(str(e)))

