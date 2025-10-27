# Copyright (c) 2025, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit import _
from creqit.model.document import Document


class FacebookLeadAds(Document):
	"""Facebook Lead Ads from Facebook Lead Ads"""
	
	def before_save(self):
		"""Set timestamps before saving"""
		if not self.created_at:
			self.created_at = creqit.utils.now()
		self.updated_at = creqit.utils.now()
	
	def on_update(self):
		"""Update timestamp on save"""
		self.updated_at = creqit.utils.now()
		super(FacebookLeadAds, self).on_update()
