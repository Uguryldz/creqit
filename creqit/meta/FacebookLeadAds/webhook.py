# Copyright (c) 2025, creqit Technologies and contributors
# License: MIT. See LICENSE

"""
Facebook Lead Ads Webhook Handler
Handles incoming webhook requests from Facebook
"""

import hashlib
import hmac
import json
import logging
import os
import requests
from datetime import datetime
from logging.handlers import RotatingFileHandler

import creqit
from creqit import _
from werkzeug.wrappers import Response

# Meta log için özel logger oluştur
def get_meta_logger():
	"""Facebook webhook logları için site-specific logger"""
	# Site adını al
	site_name = creqit.local.site or "default"
	logger_name = f"facebook_meta_logger_{site_name}"
	
	# Eğer logger zaten varsa, onu döndür
	if hasattr(creqit, f'meta_logger_{site_name}') and getattr(creqit, f'meta_logger_{site_name}'):
		return getattr(creqit, f'meta_logger_{site_name}')
	
	# Yeni logger oluştur
	logger = logging.getLogger(logger_name)
	logger.setLevel(logging.INFO)
	logger.propagate = False
	
	# Site-specific meta log dosyası için handler oluştur
	log_dir = os.path.join(creqit.utils.get_bench_path(), "logs")
	os.makedirs(log_dir, exist_ok=True)
	
	log_file = os.path.join(log_dir, f"{site_name}-meta.log")
	handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)  # 10MB, 5 backup
	
	# Formatter oluştur
	formatter = logging.Formatter(
		f'%(asctime)s - %(levelname)s - [{site_name}] - %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S'
	)
	handler.setFormatter(formatter)
	
	logger.addHandler(handler)
	
	# Logger'ı creqit'e site-specific olarak kaydet
	setattr(creqit, f'meta_logger_{site_name}', logger)
	
	return logger


@creqit.whitelist(allow_guest=True)
def handle_webhook():
	"""
	Main webhook handler for Facebook Lead Ads
	Handles both GET (verification) and POST (lead data) requests
	"""
	meta_logger = get_meta_logger()
	
	try:
		# Always log webhook requests to meta_log
		meta_logger.info(f"Facebook Webhook: {creqit.request.method} request received")
		meta_logger.info(f"Facebook Webhook: Headers: {dict(creqit.request.headers)}")
		meta_logger.info(f"Facebook Webhook: Args: {creqit.request.args}")
		meta_logger.info(f"Facebook Webhook: User-Agent: {creqit.request.headers.get('User-Agent', 'None')}")
		meta_logger.info(f"Facebook Webhook: Remote IP: {creqit.request.remote_addr}")
		
		# Ayrıca normal loglara da yaz (debugging için)
		creqit.logger().info(f"Facebook Webhook: {creqit.request.method} request received")
		
		if creqit.request.method == "GET":
			return handle_verification()
		elif creqit.request.method == "POST":
			return handle_lead_event()
		else:
			creqit.throw(_("Unsupported HTTP method"))
	except Exception as e:
		meta_logger.error(f"Facebook Webhook Error: {str(e)}")
		creqit.logger().error(f"Facebook Webhook Error: {str(e)}")
		creqit.response.status_code = 500
		return {"error": str(e)}


def handle_verification():
	"""
	Handle Facebook webhook verification (GET request)
	Facebook sends a verification request when setting up the webhook
	"""
	meta_logger = get_meta_logger()
	
	# Get query parameters
	mode = creqit.request.args.get("hub.mode")
	token = creqit.request.args.get("hub.verify_token")
	challenge = creqit.request.args.get("hub.challenge")
	
	# Log verification attempt to meta_log
	meta_logger.info(f"Facebook Webhook Verification: mode={mode}, token={token}, challenge={challenge}")
	
	# Get settings
	settings = creqit.get_single("Facebook Lead Ads Settings")
	
	# Log settings to meta_log
	meta_logger.info(f"Facebook Webhook Settings: enabled={settings.enabled}, verify_token={settings.webhook_verify_token}")
	
	# Verify token matches
	if not settings.enabled:
		meta_logger.error("Facebook Lead Ads is not enabled")
		creqit.logger().error("Facebook Lead Ads is not enabled")
		creqit.respond_as_web_page(
			"Facebook Webhook Error",
			"Facebook Lead Ads is not enabled",
			success=False
		)
		return
	
	# Detailed token comparison logging to meta_log
	expected_token = settings.webhook_verify_token
	received_token = token
	
	meta_logger.info(f"Token comparison: expected_length={len(expected_token) if expected_token else 0}, received_length={len(received_token) if received_token else 0}")
	meta_logger.info(f"Expected token repr: {repr(expected_token)}")
	meta_logger.info(f"Received token repr: {repr(received_token)}")
	
	if expected_token != received_token:
		meta_logger.error(f"Token mismatch: expected={expected_token}, received={received_token}")
		creqit.logger().error(f"Token mismatch: expected={expected_token}, received={received_token}")
		creqit.respond_as_web_page(
			"Facebook Webhook Error",
			f"Invalid verify token. Expected: {expected_token}, Received: {received_token}",
			success=False
		)
		return
	
	if mode == "subscribe":
		# Mark webhook as active
		settings.webhook_is_active = 1
		settings.save(ignore_permissions=True)
		creqit.db.commit()
		
		meta_logger.info(f"Facebook Webhook verified successfully with challenge: {challenge}")
		creqit.logger().info(f"Facebook Webhook verified successfully with challenge: {challenge}")
		
		# Facebook expects ONLY challenge string as plain text response
		# Return Flask Response directly to bypass Creqit's JSON wrapper
		return Response(challenge, status=200, mimetype='text/plain')
	
	meta_logger.error(f"Invalid mode: {mode}")
	creqit.logger().error(f"Invalid mode: {mode}")
	creqit.respond_as_web_page(
		"Facebook Webhook Error",
		"Invalid mode",
		success=False
	)
	return


def handle_lead_event():
	"""
	Handle incoming lead event from Facebook (POST request)
	"""
	meta_logger = get_meta_logger()
	
	try:
		# Parse webhook payload
		payload = creqit.request.get_json()
		
		# Log payload to meta_log
		meta_logger.info(f"Facebook Lead Event Payload: {json.dumps(payload, indent=2)}")
		
		if not payload:
			meta_logger.error("Invalid payload received")
			creqit.response.status_code = 400
			return {"error": "Invalid payload"}
		
		# Check if it's a page event
		if payload.get("object") != "page":
			meta_logger.info(f"Non-page event received: {payload.get('object')}")
			creqit.response.status_code = 200
			return {"success": True}
		
		# Process each entry
		for entry in payload.get("entry", []):
			process_entry(entry)
		
		# Return success response
		meta_logger.info("Facebook Lead Event processed successfully")
		creqit.response.status_code = 200
		return {"success": True}
		
	except Exception as e:
		meta_logger.error(f"Facebook Lead Event Processing Error: {str(e)}")
		creqit.logger().error(f"Facebook Lead Event Processing Error: {str(e)}")
		creqit.response.status_code = 500
		return {"error": str(e)}


def process_entry(entry):
	"""
	Process a single webhook entry
	
	Args:
		entry: Webhook entry data from Facebook
	"""
	meta_logger = get_meta_logger()
	
	entry_id = entry.get("id")
	changes = entry.get("changes", [])
	
	meta_logger.info(f"Processing entry {entry_id} with {len(changes)} changes")
	
	for change in changes:
		# Check if it's a leadgen event
		if change.get("field") != "leadgen":
			meta_logger.info(f"Skipping non-leadgen change: {change.get('field')}")
			continue
		
		value = change.get("value", {})
		page_id = value.get("page_id")
		form_id = value.get("form_id")
		leadgen_id = value.get("leadgen_id")
		
		# Log the lead event to meta_log
		meta_logger.info(f"Received lead {leadgen_id} from page {page_id}, form {form_id}")
		meta_logger.info(f"Lead data: {json.dumps(value, indent=2)}")
		
		# Create Facebook Lead Ads document with detailed data
		create_facebook_lead_ads(leadgen_id, page_id, form_id, value)
		
		# Publish realtime event
		creqit.publish_realtime(
			event="facebook_lead_received",
			message={
				"leadgen_id": leadgen_id,
				"page_id": page_id,
				"form_id": form_id,
				"timestamp": creqit.utils.now()
			},
			user=creqit.session.user
		)


def create_facebook_lead_ads(leadgen_id, page_id, form_id, webhook_data):
	"""
	Create a Facebook Lead Ads document from webhook data with detailed Facebook API data
	
	Args:
		leadgen_id: Facebook lead ID
		page_id: Facebook page ID
		form_id: Facebook form ID
		webhook_data: Raw webhook data
	"""
	meta_logger = get_meta_logger()
	
	try:
		# Check if Facebook Lead Ads DocType exists
		if not creqit.db.exists("DocType", "Facebook Lead Ads"):
			meta_logger.warning("Facebook Lead Ads DocType not found, skipping lead creation")
			creqit.logger().warning("Facebook Lead Ads DocType not found, skipping lead creation")
			return
		
		# Check if lead already exists
		if creqit.db.exists("Facebook Lead Ads", {"facebook_lead_id": leadgen_id}):
			meta_logger.info(f"Facebook Lead Ads {leadgen_id} already exists, skipping")
			creqit.logger().info(f"Facebook Lead Ads {leadgen_id} already exists, skipping")
			return
		
		# Get Facebook API settings
		settings = creqit.get_single("Facebook Lead Ads Settings")
		if not settings.enabled or not settings.access_token:
			meta_logger.error("Facebook Lead Ads is not enabled or access token not configured")
			return
		
		# Fetch detailed lead data from Facebook API
		lead_details = fetch_lead_details_from_facebook(leadgen_id, page_id, form_id, settings.access_token)
		
		# Create Facebook Lead Ads document
		lead_doc = creqit.get_doc({
			"doctype": "Facebook Lead Ads",
			"lead_id": f"FB-{leadgen_id}",
			"status": "New",
			"facebook_lead_id": leadgen_id,
			"facebook_form_id": form_id,
			"facebook_form_name": lead_details.get("form_name"),
			"facebook_form_status": lead_details.get("form_status"),
			"facebook_page_id": page_id,
			"facebook_page_name": lead_details.get("page_name"),
			"facebook_ad_id": lead_details.get("ad_id"),
			"facebook_adset_id": lead_details.get("adset_id"),
			"facebook_campaign_id": lead_details.get("campaign_id"),
			"lead_data": json.dumps(webhook_data, indent=2),
			"field_data": json.dumps(lead_details.get("field_data", []), indent=2),
			"created_at": creqit.utils.now()
		})
		
		lead_doc.insert(ignore_permissions=True)
		creqit.db.commit()
		
		meta_logger.info(f"Created Facebook Lead Ads {lead_doc.name} for lead {leadgen_id}")
		creqit.logger().info(f"Created Facebook Lead Ads {lead_doc.name} for lead {leadgen_id}")
		
		# Otomatik form oluşturma
		create_automatic_form(lead_doc, lead_details)
		
	except Exception as e:
		meta_logger.error(f"Failed to create Facebook Lead Ads: {str(e)}")
		creqit.logger().error(f"Failed to create Facebook Lead Ads: {str(e)}")


def fetch_lead_details_from_facebook(leadgen_id, page_id, form_id, access_token):
	"""
	Fetch detailed lead data from Facebook Graph API
	
	Args:
		leadgen_id: Facebook lead ID
		page_id: Facebook page ID
		form_id: Facebook form ID
		access_token: Facebook access token
		
	Returns:
		dict: Detailed lead data from Facebook API
	"""
	meta_logger = get_meta_logger()
	base_url = "https://graph.facebook.com/v24.0"
	final_data = {}
	
	try:
		# 1. Leadgen Nesnesini Çekme (Müşteri Cevapları ve Ad ID)
		lead_fields = "field_data,ad_id"
		lead_url = f"{base_url}/{leadgen_id}?fields={lead_fields}&access_token={access_token}"
		
		meta_logger.info(f"Fetching lead data from: {lead_url}")
		lead_response = requests.get(lead_url).json()
		
		if 'error' in lead_response:
			meta_logger.error(f"Lead data error: {lead_response['error']['message']}")
			final_data['error'] = f"Lead Verisi Hatası: {lead_response['error']['message']}"
			return final_data
		
		final_data.update(lead_response)
		
		# 2. Form Adını ve Status'unu Çekme
		form_url = f"{base_url}/{form_id}?fields=name,status&access_token={access_token}"
		meta_logger.info(f"Fetching form details from: {form_url}")
		
		try:
			form_response = requests.get(form_url, timeout=10).json()
			meta_logger.info(f"Form response: {json.dumps(form_response, indent=2)}")
			
			if 'error' in form_response:
				meta_logger.error(f"Form API error: {form_response['error']}")
				final_data['form_name'] = f"Form {form_id}"
				final_data['form_status'] = "ERROR"
			else:
				if 'name' in form_response:
					final_data['form_name'] = form_response['name']
					meta_logger.info(f"Form name retrieved: {form_response['name']}")
				else:
					meta_logger.warning(f"No form name found in response: {form_response}")
					final_data['form_name'] = f"Form {form_id}"
				
				if 'status' in form_response:
					final_data['form_status'] = form_response['status']
					meta_logger.info(f"Form status retrieved: {form_response['status']}")
				else:
					meta_logger.warning(f"No form status found in response: {form_response}")
					final_data['form_status'] = "UNKNOWN"
		except Exception as e:
			meta_logger.error(f"Form API request failed: {str(e)}")
			final_data['form_name'] = f"Form {form_id}"
			final_data['form_status'] = "ERROR"
		
		# 3. Sayfa Adını Çekme
		page_url = f"{base_url}/{page_id}?fields=name&access_token={access_token}"
		meta_logger.info(f"Fetching page name from: {page_url}")
		
		try:
			page_response = requests.get(page_url, timeout=10).json()
			meta_logger.info(f"Page response: {json.dumps(page_response, indent=2)}")
			
			if 'error' in page_response:
				meta_logger.error(f"Page API error: {page_response['error']}")
				final_data['page_name'] = f"Page {page_id}"
			else:
				if 'name' in page_response:
					final_data['page_name'] = page_response['name']
					meta_logger.info(f"Page name retrieved: {page_response['name']}")
				else:
					meta_logger.warning(f"No page name found in response: {page_response}")
					final_data['page_name'] = f"Page {page_id}"
		except Exception as e:
			meta_logger.error(f"Page API request failed: {str(e)}")
			final_data['page_name'] = f"Page {page_id}"
		
		# 4. Reklam Detaylarını Çekme (Yalnızca ad_id mevcutsa ve organik değilse)
		if final_data.get('ad_id') and not final_data.get('is_organic'):
			ad_id = final_data['ad_id']
			ad_fields = "name,adset{name,campaign{name}}"
			ad_url = f"{base_url}/{ad_id}?fields={ad_fields}&access_token={access_token}"
			
			meta_logger.info(f"Fetching ad details from: {ad_url}")
			ad_response = requests.get(ad_url).json()
			
			if 'error' not in ad_response and 'adset' in ad_response:
				final_data['ad_name'] = ad_response.get('name')
				final_data['adset_name'] = ad_response['adset'].get('name')
				final_data['campaign_name'] = ad_response['adset']['campaign'].get('name')
				final_data['campaign_id'] = ad_response['adset']['campaign'].get('id')
			elif 'error' in ad_response:
				final_data['ad_error'] = ad_response['error']['message']
				meta_logger.error(f"Ad details error: {ad_response['error']['message']}")
		
		meta_logger.info(f"Successfully fetched lead details for {leadgen_id}")
		return final_data
		
	except Exception as e:
		meta_logger.error(f"Error fetching lead details from Facebook: {str(e)}")
		creqit.logger().error(f"Error fetching lead details from Facebook: {str(e)}")
		return {"error": str(e)}


def create_automatic_form(lead_doc, lead_details):
	"""
	Otomatik form oluşturma mekanizması
	Facebook Lead Ads verilerini kullanarak otomatik form oluşturur
	
	Args:
		lead_doc: Facebook Lead Ads document
		lead_details: Facebook API'den gelen detaylı veriler
	"""
	meta_logger = get_meta_logger()
	
	try:
		# Form oluşturma ayarlarını kontrol et
		settings = creqit.get_single("Facebook Lead Ads Settings")
		if not settings.auto_create_forms:
			meta_logger.info("Auto create forms is disabled, skipping form creation")
			return
		
		# Form adı oluştur
		form_name = f"FB-{lead_doc.facebook_lead_id}-{lead_doc.form_name or 'Form'}"
		form_name = form_name.replace(" ", "-").replace("/", "-")[:50]  # URL-safe ve kısa
		
		# Mevcut form kontrolü
		if creqit.db.exists("Web Form", {"title": form_name}):
			meta_logger.info(f"Form {form_name} already exists, skipping creation")
			return
		
		# Field data'dan form alanları oluştur
		field_data = lead_details.get("field_data", [])
		if not field_data:
			meta_logger.warning(f"No field data available for form creation: {lead_doc.facebook_lead_id}")
			return
		
		# Web Form oluştur
		web_form = creqit.get_doc({
			"doctype": "Web Form",
			"title": form_name,
			"route": f"facebook-lead-{lead_doc.facebook_lead_id}",
			"published": 1,
			"allow_edit": 0,
			"allow_multiple": 0,
			"allow_delete": 0,
			"show_attachments": 0,
			"allow_comments": 0,
			"doc_type": "Facebook Lead Ads",
			"is_standard": 0,
			"introduction_text": f"Facebook Lead Form - {lead_doc.form_name or 'Form'}",
			"success_message": "Form submitted successfully!",
			"success_url": "/",
			"meta_title": form_name,
			"meta_description": f"Facebook Lead Form for {lead_doc.form_name or 'Form'}",
			"client_script": get_form_client_script(),
			"custom_css": get_form_custom_css()
		})
		
		# Form alanlarını oluştur
		create_form_fields(web_form, field_data)
		
		# Form'u kaydet
		web_form.insert(ignore_permissions=True)
		creqit.db.commit()
		
		# Lead document'ı güncelle
		lead_doc.auto_created_form = web_form.name
		lead_doc.save(ignore_permissions=True)
		creqit.db.commit()
		
		meta_logger.info(f"Created automatic form {web_form.name} for lead {lead_doc.facebook_lead_id}")
		creqit.logger().info(f"Created automatic form {web_form.name} for lead {lead_doc.facebook_lead_id}")
		
	except Exception as e:
		meta_logger.error(f"Failed to create automatic form: {str(e)}")
		creqit.logger().error(f"Failed to create automatic form: {str(e)}")


def create_form_fields(web_form, field_data):
	"""
	Facebook field data'dan form alanları oluştur
	
	Args:
		web_form: Web Form document
		field_data: Facebook field data listesi
	"""
	meta_logger = get_meta_logger()
	
	# Field mapping - Facebook field names to form field types
	field_mapping = {
		"full_name": {"fieldtype": "Data", "label": "Full Name", "reqd": 1},
		"first_name": {"fieldtype": "Data", "label": "First Name", "reqd": 1},
		"last_name": {"fieldtype": "Data", "label": "Last Name", "reqd": 1},
		"email": {"fieldtype": "Data", "label": "Email", "reqd": 1},
		"phone_number": {"fieldtype": "Data", "label": "Phone Number", "reqd": 0},
		"city": {"fieldtype": "Data", "label": "City", "reqd": 0},
		"state": {"fieldtype": "Data", "label": "State", "reqd": 0},
		"zip_code": {"fieldtype": "Data", "label": "ZIP Code", "reqd": 0},
		"country": {"fieldtype": "Data", "label": "Country", "reqd": 0},
		"company": {"fieldtype": "Data", "label": "Company", "reqd": 0},
		"job_title": {"fieldtype": "Data", "label": "Job Title", "reqd": 0},
		"message": {"fieldtype": "Text", "label": "Message", "reqd": 0},
		"comments": {"fieldtype": "Text", "label": "Comments", "reqd": 0},
		"budget": {"fieldtype": "Select", "label": "Budget", "reqd": 0, "options": "Under $1000\n$1000-$5000\n$5000-$10000\nOver $10000"},
		"interest": {"fieldtype": "Select", "label": "Interest", "reqd": 0, "options": "Product Information\nPricing\nDemo\nSupport\nOther"},
		"source": {"fieldtype": "Data", "label": "Source", "reqd": 0, "read_only": 1}
	}
	
	for field in field_data:
		field_name = field.get("name", "").lower().replace(" ", "_")
		field_value = field.get("values", [""])[0] if field.get("values") else ""
		
		# Field mapping'den alan tipini al
		field_config = field_mapping.get(field_name, {
			"fieldtype": "Data", 
			"label": field.get("name", "Unknown Field").title(),
			"reqd": 0
		})
		
		# Web Form Field oluştur
		web_form_field = {
			"doctype": "Web Form Field",
			"fieldname": field_name,
			"fieldtype": field_config["fieldtype"],
			"label": field_config["label"],
			"reqd": field_config["reqd"],
			"options": field_config.get("options", ""),
			"read_only": field_config.get("read_only", 0),
			"default": field_value if field_config.get("read_only") else ""
		}
		
		web_form.append("web_form_fields", web_form_field)
		meta_logger.info(f"Added form field: {field_name} ({field_config['fieldtype']})")


def get_form_client_script():
	"""
	Form için client script döndür
	"""
	return """
// Facebook Lead Form Client Script
frappe.ready(function() {
	// Form submit edildiğinde Facebook Lead Ads document'ı oluştur
	$('.web-form-wrapper').on('submit', 'form', function(e) {
		e.preventDefault();
		
		// Form verilerini topla
		var form_data = {};
		$(this).find('input, textarea, select').each(function() {
			if ($(this).attr('name')) {
				form_data[$(this).attr('name')] = $(this).val();
			}
		});
		
		// Facebook Lead Ads document'ı oluştur
		frappe.call({
			method: 'creqit.meta.FacebookLeadAds.webhook.create_lead_from_form',
			args: {
				form_data: form_data,
				form_name: '$(this).attr("data-web-form")'
			},
			callback: function(r) {
				if (r.message) {
					frappe.show_alert({
						message: 'Form submitted successfully!',
						indicator: 'green'
					});
					// Form'u temizle
					$(this)[0].reset();
				}
			}
		});
	});
});
"""


def get_form_custom_css():
	"""
	Form için custom CSS döndür
	"""
	return """
/* Facebook Lead Form Custom CSS */
.web-form-wrapper {
	max-width: 600px;
	margin: 0 auto;
	padding: 20px;
}

.web-form-wrapper .form-group {
	margin-bottom: 20px;
}

.web-form-wrapper label {
	font-weight: bold;
	margin-bottom: 5px;
	display: block;
}

.web-form-wrapper input,
.web-form-wrapper textarea,
.web-form-wrapper select {
	width: 100%;
	padding: 10px;
	border: 1px solid #ddd;
	border-radius: 4px;
	font-size: 14px;
}

.web-form-wrapper button[type="submit"] {
	background-color: #1877f2;
	color: white;
	padding: 12px 24px;
	border: none;
	border-radius: 4px;
	font-size: 16px;
	cursor: pointer;
	width: 100%;
}

.web-form-wrapper button[type="submit"]:hover {
	background-color: #166fe5;
}
"""


@creqit.whitelist(allow_guest=True)
def create_lead_from_form(form_data, form_name):
	"""
	Form'dan gelen verilerle Facebook Lead Ads document'ı oluştur
	
	Args:
		form_data: Form verileri
		form_name: Form adı
	"""
	meta_logger = get_meta_logger()
	
	try:
		# Facebook Lead Ads document'ı oluştur
		lead_doc = creqit.get_doc({
			"doctype": "Facebook Lead Ads",
			"lead_id": f"FORM-{creqit.utils.now().strftime('%Y%m%d%H%M%S')}",
			"status": "New",
			"form_name": form_name,
			"field_data": json.dumps(form_data, indent=2),
			"created_at": creqit.utils.now()
		})
		
		lead_doc.insert(ignore_permissions=True)
		creqit.db.commit()
		
		meta_logger.info(f"Created Facebook Lead Ads from form: {lead_doc.name}")
		return {"success": True, "lead_id": lead_doc.name}
		
	except Exception as e:
		meta_logger.error(f"Failed to create lead from form: {str(e)}")
		return {"success": False, "error": str(e)}


@creqit.whitelist()
def test_lead_creation():
	"""
	Test lead creation with sample data
	"""
	meta_logger = get_meta_logger()
	
	try:
		# Sample webhook data
		sample_webhook_data = {
			"created_time": 1761599000,
			"leadgen_id": "TEST123456789",
			"page_id": "630764346787767",
			"form_id": "1912140606324258"
		}
		
		meta_logger.info(f"Testing lead creation with sample data: {json.dumps(sample_webhook_data, indent=2)}")
		
		# Test the creation process
		create_facebook_lead_ads(
			sample_webhook_data["leadgen_id"],
			sample_webhook_data["page_id"],
			sample_webhook_data["form_id"],
			sample_webhook_data
		)
		
		return {"success": True, "message": "Test lead creation completed"}
		
	except Exception as e:
		meta_logger.error(f"Test lead creation error: {str(e)}")
		return {"error": str(e)}


@creqit.whitelist()
def test_facebook_api():
	"""
	Test Facebook API calls for form and page data
	"""
	meta_logger = get_meta_logger()
	
	try:
		settings = creqit.get_single("Facebook Lead Ads Settings")
		if not settings.enabled or not settings.access_token:
			return {"error": "Facebook Lead Ads is not enabled or access token not configured"}
		
		access_token = settings.access_token
		base_url = "https://graph.facebook.com/v24.0"
		
		# Test form API call
		form_id = "1912140606324258"  # Test form ID
		form_url = f"{base_url}/{form_id}?fields=name,status&access_token={access_token}"
		
		meta_logger.info(f"Testing form API: {form_url}")
		form_response = requests.get(form_url).json()
		
		# Test page API call
		page_id = "630764346787767"  # Test page ID
		page_url = f"{base_url}/{page_id}?fields=name&access_token={access_token}"
		
		meta_logger.info(f"Testing page API: {page_url}")
		page_response = requests.get(page_url).json()
		
		return {
			"success": True,
			"form_api": {
				"url": form_url,
				"response": form_response,
				"has_name": "name" in form_response,
				"has_status": "status" in form_response,
				"form_name": form_response.get("name"),
				"form_status": form_response.get("status")
			},
			"page_api": {
				"url": page_url,
				"response": page_response,
				"has_name": "name" in page_response,
				"page_name": page_response.get("name")
			}
		}
		
	except Exception as e:
		meta_logger.error(f"Test Facebook API error: {str(e)}")
		return {"error": str(e)}


@creqit.whitelist()
def test_webhook():
	"""Test webhook configuration"""
	settings = creqit.get_single("Facebook Lead Ads Settings")
	
	return {
		"webhook_url": settings.webhook_callback_url,
		"verify_token": settings.webhook_verify_token,
		"is_active": settings.webhook_is_active,
		"enabled": settings.enabled
	}

@creqit.whitelist()
def test_meta_logger():
	"""Test meta logger functionality"""
	meta_logger = get_meta_logger()
	
	# Test log yazma
	meta_logger.info("Meta logger test - INFO level")
	meta_logger.warning("Meta logger test - WARNING level")
	meta_logger.error("Meta logger test - ERROR level")
	
	# Site-specific meta log dosyasının varlığını kontrol et
	site_name = creqit.local.site or "default"
	meta_log_file = os.path.join(creqit.utils.get_bench_path(), "logs", f"{site_name}-meta.log")
	
	return {
		"meta_log_file": meta_log_file,
		"site_name": site_name,
		"file_exists": os.path.exists(meta_log_file),
		"test_logs_written": True
	}

@creqit.whitelist(allow_guest=True)
def webhook_logs():
	"""View webhook logs - for debugging"""
	import os
	import glob
	
	# Site-specific meta log dosyasını kontrol et
	site_name = creqit.local.site or "default"
	meta_log_file = os.path.join(creqit.utils.get_bench_path(), "logs", f"{site_name}-meta.log")
	
	if os.path.exists(meta_log_file):
		# Site-specific meta log dosyasından oku
		with open(meta_log_file, 'r') as f:
			lines = f.readlines()
			last_lines = lines[-100:] if len(lines) > 100 else lines
		
		return {
			"log_file": meta_log_file,
			"site_name": site_name,
			"total_lines": len(lines),
			"webhook_entries": len(last_lines),
			"recent_webhook_logs": last_lines[-20:] if last_lines else [],
			"log_type": "site_specific_meta_log"
		}
	else:
		# Fallback: normal log dosyalarından ara
		log_files = glob.glob("/home/uyildiz/creqit/creqit-env/creqit/logs/*.log")
		latest_log = max(log_files, key=os.path.getctime) if log_files else None
		
		if not latest_log:
			return {"error": "No log files found"}
		
		# Read last 100 lines
		with open(latest_log, 'r') as f:
			lines = f.readlines()
			last_lines = lines[-100:] if len(lines) > 100 else lines
		
		# Filter Facebook webhook related lines
		webhook_lines = [line for line in last_lines if 'Facebook Webhook' in line]
		
		return {
			"log_file": latest_log,
			"site_name": site_name,
			"total_lines": len(lines),
			"webhook_entries": len(webhook_lines),
			"recent_webhook_logs": webhook_lines[-20:] if webhook_lines else [],
			"log_type": "general_log"
		}

