# Copyright (c) 2024, Agile Shift and contributors
# For license information, please see license.txt

# import frappe
from frappe.utils.nestedset import NestedSet


class AgentGroup(NestedSet):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.party_account.party_account import PartyAccount
		from erpnext.selling.doctype.customer_credit_limit.customer_credit_limit import CustomerCreditLimit
		from frappe.types import DF

		accounts: DF.Table[PartyAccount]
		agent_group_name: DF.Data
		commission_rate: DF.Float
		credit_limits: DF.Table[CustomerCreditLimit]
		default_price_list: DF.Link | None
		is_group: DF.Check
		lft: DF.Int
		old_parent: DF.Link | None
		parent_customer_group: DF.Link | None
		payment_terms: DF.Link | None
		rgt: DF.Int
	# end: auto-generated types
	pass
