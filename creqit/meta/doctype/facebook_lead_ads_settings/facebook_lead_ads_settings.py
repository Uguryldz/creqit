# Copyright (c) 2025, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit import _
from creqit.model.document import Document


class FacebookLeadAdsSettings(Document):
	"""Facebook Lead Ads Settings for OAuth2 integration"""

	def validate(self):
		"""Validate settings before saving"""
		if self.enabled:
			if not self.app_id:
				creqit.throw(_("App ID is required when Facebook Lead Ads is enabled"))
			if not self.app_secret:
				creqit.throw(_("App Secret is required when Facebook Lead Ads is enabled"))
	
	def before_save(self):
		"""Generate webhook credentials before saving"""
		if self.enabled:
			# Generate webhook callback URL
			site_url = creqit.utils.get_url()
			self.webhook_callback_url = f"{site_url}/api/method/creqit.meta.FacebookLeadAds.webhook.handle_webhook"
			
			# Generate verify token if not exists
			if not self.webhook_verify_token:
				self.webhook_verify_token = creqit.generate_hash(length=32)

	def get_access_token(self):
		"""Get the current access token"""
		return self.access_token

	def set_access_token(self, token, expiry=None):
		"""Set the access token"""
		# Set access token directly since it's now a Data field
		self.access_token = token
		if expiry:
			from datetime import datetime, timedelta
			if isinstance(expiry, int):
				# If expiry is seconds, convert to datetime
				expiry = datetime.now() + timedelta(seconds=expiry)
			elif isinstance(expiry, str):
				# If expiry is string, try to parse it
				try:
					expiry = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
				except:
					# If parsing fails, use current time + 1 hour as fallback
					expiry = datetime.now() + timedelta(hours=1)
			self.token_expiry = expiry
		else:
			# For long-lived tokens (no expiry), set to None
			self.token_expiry = None
		
		# Save without triggering validation
		self.flags.ignore_validate = True
		self.save(ignore_permissions=True)
		creqit.db.commit()

	@creqit.whitelist()
	def start_oauth_flow(self):
		"""Start OAuth2 flow and return authorization URL"""
		from creqit.meta.FacebookLeadAds.oauth import get_authorization_url
		return get_authorization_url()
	
	@creqit.whitelist()
	def get_token_status(self):
		"""Get current token status"""
		from creqit.meta.FacebookLeadAds.oauth import get_token_info
		return get_token_info()
	
	@creqit.whitelist()
	def refresh_access_token(self):
		"""Refresh the access token"""
		from creqit.meta.FacebookLeadAds.oauth import refresh_token
		return refresh_token()
	
	@creqit.whitelist()
	def regenerate_verify_token(self):
		"""Regenerate webhook verify token"""
		self.webhook_verify_token = creqit.generate_hash(length=32)
		self.webhook_is_active = 0
		self.save(ignore_permissions=True)
		return {
			"message": _("Verify token regenerated. Please update it in Facebook."),
			"verify_token": self.webhook_verify_token
		}

