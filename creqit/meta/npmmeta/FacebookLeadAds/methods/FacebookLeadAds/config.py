# Copyright (c) 2025, creqit Technologies and contributors
# License: MIT. See LICENSE

"""
Configuration file for Facebook Lead Ads Integration
"""

from creqit import _

def get_data():
	"""Return configuration data for the module"""
	return [
		{
			"module_name": "FacebookLeadAds",
			"category": "Modules",
			"label": _("Facebook Lead Ads"),
			"color": "#3b5998",  # Facebook blue
			"icon": "octicon octicon-megaphone",
			"type": "module",
			"description": _("Facebook Lead Ads Integration")
		}
	]

