# Copyright (c) 2024, Agile Shift and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AccountGroup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from cargo_management.cargo_management.doctype.group_of_account.group_of_account import GroupofAccount
		from frappe.types import DF

		account: DF.Table[GroupofAccount]
		type_name: DF.Data
	# end: auto-generated types
	pass
