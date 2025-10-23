# Copyright (c) 2019, creqit Technologies and contributors
# License: MIT. See LICENSE

# import creqit
from creqit.model.document import Document


class LDAPGroupMapping(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from creqit.types import DF

		creqit_role: DF.Link
		ldap_group: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	pass
