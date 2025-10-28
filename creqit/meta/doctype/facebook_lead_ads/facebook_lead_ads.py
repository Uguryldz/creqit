# Copyright (c) 2025, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit import _
from creqit.model.document import Document
import json
from datetime import datetime


class FacebookLeadAds(Document):
	"""Facebook Lead Ads from Facebook Lead Ads"""
	
	def before_save(self):
		"""Set timestamps before saving"""
		# Parse created_time from lead_data if exists
		if self.lead_data and not self.created_at:
			try:
				lead_data_dict = json.loads(self.lead_data) if isinstance(self.lead_data, str) else self.lead_data
				if 'created_time' in lead_data_dict:
					timestamp = int(lead_data_dict['created_time'])
					dt = datetime.fromtimestamp(timestamp)
					self.created_at = dt.strftime('%d.%m.%Y %H:%M')
			except (json.JSONDecodeError, ValueError, KeyError):
				pass
		
		if not self.created_at:
			self.created_at = creqit.utils.now()
		self.updated_at = creqit.utils.now()
	
	def on_update(self):
		"""Update timestamp on save"""
		self.updated_at = creqit.utils.now()
		super(FacebookLeadAds, self).on_update()
