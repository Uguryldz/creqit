# Copyright (c) 2025, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit import _
from creqit.model.document import Document


class FacebookLeadAdsWebhook(Document):
	"""Facebook Lead Ads Webhook for receiving lead notifications"""

	def autoname(self):
		"""Auto name the document"""
		if not self.webhook_name:
			self.webhook_name = f"{self.page_id}_{self.form_id}"

	def validate(self):
		"""Validate webhook before saving"""
		if self.enabled:
			# Check if Facebook Lead Ads Settings is enabled
			settings = creqit.get_single("Facebook Lead Ads Settings")
			if not settings.enabled:
				creqit.throw(_("Please enable Facebook Lead Ads Settings first"))

			if not self.page_id:
				creqit.throw(_("Page ID is required"))
			if not self.form_id:
				creqit.throw(_("Form ID is required"))

	def before_insert(self):
		"""Setup webhook before insert"""
		# Generate verify token
		self.verify_token = creqit.generate_hash(length=32)
		
		# Set webhook URL
		site_url = creqit.utils.get_url()
		self.webhook_url = f"{site_url}/api/method/creqit.meta.FacebookLeadAds.webhook.handle_webhook"

	def on_update(self):
		"""Update webhook subscription on Facebook"""
		if self.has_value_changed("enabled"):
			if self.enabled:
				self.subscribe_webhook()
			else:
				self.unsubscribe_webhook()

	def on_trash(self):
		"""Unsubscribe webhook on delete"""
		if self.is_active:
			self.unsubscribe_webhook()

	def subscribe_webhook(self):
		"""Subscribe webhook on Facebook"""
		from creqit.meta.FacebookLeadAds.utils import (
			create_app_webhook_subscription,
			install_app_on_page
		)

		try:
			# Create webhook subscription
			settings = creqit.get_single("Facebook Lead Ads Settings")
			
			subscription = create_app_webhook_subscription(
				app_id=settings.app_id,
				callback_url=self.webhook_url,
				verify_token=self.verify_token,
				fields=["leadgen"],
				include_values=True
			)

			# Install app on page
			install_app_on_page(self.page_id, "leadgen")

			# Update subscription status
			self.is_active = 1
			self.subscription_id = subscription.get("id")
			self.save(ignore_permissions=True)

			creqit.msgprint(_("Webhook subscription created successfully"))
		except Exception as e:
			creqit.log_error("Facebook Webhook Subscription Error")
			creqit.throw(_("Failed to subscribe webhook: {0}").format(str(e)))

	def unsubscribe_webhook(self):
		"""Unsubscribe webhook from Facebook"""
		from creqit.meta.FacebookLeadAds.utils import delete_app_webhook_subscription

		try:
			settings = creqit.get_single("Facebook Lead Ads Settings")
			delete_app_webhook_subscription(settings.app_id, "page")

			self.is_active = 0
			self.subscription_id = None
			self.save(ignore_permissions=True)

			creqit.msgprint(_("Webhook subscription removed successfully"))
		except Exception as e:
			creqit.log_error("Facebook Webhook Unsubscription Error")
			creqit.throw(_("Failed to unsubscribe webhook: {0}").format(str(e)))

	def process_lead(self, lead_data):
		"""Process incoming lead data"""
		try:
			# Increment lead count
			self.lead_count = (self.lead_count or 0) + 1
			self.last_lead_received = creqit.utils.now()
			self.save(ignore_permissions=True)

			# Emit event for lead processing
			creqit.publish_realtime(
				event="facebook_lead_received",
				message=lead_data,
				user=creqit.session.user
			)

			return lead_data
		except Exception as e:
			creqit.log_error("Facebook Lead Processing Error")
			raise

