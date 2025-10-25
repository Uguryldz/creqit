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

	def get_access_token(self):
		"""Get the current access token"""
		if self.access_token:
			return self.get_password("access_token")
		return None

	def set_access_token(self, token, expiry=None):
		"""Set the access token"""
		# Use set_password for Password field
		self.set("access_token", token)
		if expiry:
			from datetime import datetime
			if isinstance(expiry, int):
				# If expiry is seconds, convert to datetime
				from datetime import timedelta
				expiry = datetime.now() + timedelta(seconds=expiry)
			self.token_expiry = expiry
		
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

