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
		
		# Create Facebook Lead document
		create_facebook_lead(leadgen_id, page_id, form_id, value)
		
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


def create_facebook_lead(leadgen_id, page_id, form_id, webhook_data):
	"""
	Create a Facebook Lead document from webhook data
	
	Args:
		leadgen_id: Facebook lead ID
		page_id: Facebook page ID
		form_id: Facebook form ID
		webhook_data: Raw webhook data
	"""
	meta_logger = get_meta_logger()
	
	try:
		# Check if Facebook Lead DocType exists
		if not creqit.db.exists("DocType", "Facebook Lead"):
			meta_logger.warning("Facebook Lead DocType not found, skipping lead creation")
			creqit.logger().warning("Facebook Lead DocType not found, skipping lead creation")
			return
		
		# Check if lead already exists
		if creqit.db.exists("Facebook Lead", {"facebook_lead_id": leadgen_id}):
			meta_logger.info(f"Facebook Lead {leadgen_id} already exists, skipping")
			creqit.logger().info(f"Facebook Lead {leadgen_id} already exists, skipping")
			return
		
		# Create Facebook Lead document
		lead_doc = creqit.get_doc({
			"doctype": "Facebook Lead",
			"lead_id": f"FB-{leadgen_id}",
			"status": "New",
			"facebook_lead_id": leadgen_id,
			"facebook_form_id": form_id,
			"facebook_page_id": page_id,
			"facebook_ad_id": webhook_data.get("ad_id"),
			"facebook_adset_id": webhook_data.get("adset_id"),
			"lead_data": json.dumps(webhook_data, indent=2),
			"created_at": creqit.utils.now()
		})
		
		lead_doc.insert(ignore_permissions=True)
		creqit.db.commit()
		
		meta_logger.info(f"Created Facebook Lead {lead_doc.name} for lead {leadgen_id}")
		creqit.logger().info(f"Created Facebook Lead {lead_doc.name} for lead {leadgen_id}")
		
	except Exception as e:
		meta_logger.error(f"Failed to create Facebook Lead: {str(e)}")
		creqit.logger().error(f"Failed to create Facebook Lead: {str(e)}")


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

