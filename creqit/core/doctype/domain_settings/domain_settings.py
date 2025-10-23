# Copyright (c) 2017, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit.model.document import Document


class DomainSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from creqit.core.doctype.has_domain.has_domain import HasDomain
		from creqit.types import DF

		active_domains: DF.Table[HasDomain]
	# end: auto-generated types

	def set_active_domains(self, domains):
		active_domains = [d.domain for d in self.active_domains]
		added = False
		for d in domains:
			if d not in active_domains:
				self.append("active_domains", dict(domain=d))
				added = True

		if added:
			self.save()

	def on_update(self):
		for i, d in enumerate(self.active_domains):
			# set the flag to update the the desktop icons of all domains
			if i >= 1:
				creqit.flags.keep_desktop_icons = True
			domain = creqit.get_doc("Domain", d.domain)
			domain.setup_domain()

		self.restrict_roles_and_modules()
		creqit.clear_cache()

	def restrict_roles_and_modules(self):
		"""Disable all restricted roles and set `restrict_to_domain` property in Module Def"""
		active_domains = creqit.get_active_domains()
		all_domains = list(creqit.get_hooks("domains") or {})

		def remove_role(role):
			creqit.db.delete("Has Role", {"role": role})
			creqit.set_value("Role", role, "disabled", 1)

		for domain in all_domains:
			data = creqit.get_domain_data(domain)
			if not creqit.db.get_value("Domain", domain):
				creqit.get_doc(doctype="Domain", domain=domain).insert()
			if "modules" in data:
				for module in data.get("modules"):
					creqit.db.set_value("Module Def", module, "restrict_to_domain", domain)

			if "restricted_roles" in data:
				for role in data["restricted_roles"]:
					if not creqit.db.get_value("Role", role):
						creqit.get_doc(doctype="Role", role_name=role).insert()
					creqit.db.set_value("Role", role, "restrict_to_domain", domain)

					if domain not in active_domains:
						remove_role(role)

			if "custom_fields" in data:
				if domain not in active_domains:
					inactive_domain = creqit.get_doc("Domain", domain)
					inactive_domain.setup_data()
					inactive_domain.remove_custom_field()


def get_active_domains():
	"""get the domains set in the Domain Settings as active domain"""

	def _get_active_domains():
		domains = creqit.get_all(
			"Has Domain", filters={"parent": "Domain Settings"}, fields=["domain"], distinct=True
		)

		active_domains = [row.get("domain") for row in domains]
		active_domains.append("")
		return active_domains

	return creqit.cache.get_value("active_domains", _get_active_domains)


def get_active_modules():
	"""get the active modules from Module Def"""

	def _get_active_modules():
		active_modules = []
		active_domains = get_active_domains()
		for m in creqit.get_all("Module Def", fields=["name", "restrict_to_domain"]):
			if (not m.restrict_to_domain) or (m.restrict_to_domain in active_domains):
				active_modules.append(m.name)
		return active_modules

	return creqit.cache.get_value("active_modules", _get_active_modules)
