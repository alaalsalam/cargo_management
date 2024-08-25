# Copyright (c) 2024, Agile Shift and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from erpnext.controllers.website_list_for_contact import add_role_for_portal_user
from erpnext.accounts.party import get_dashboard_info, validate_party_accounts



class Agent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.allowed_to_transact_with.allowed_to_transact_with import AllowedToTransactWith
		from erpnext.accounts.doctype.party_account.party_account import PartyAccount
		from erpnext.selling.doctype.customer_credit_limit.customer_credit_limit import CustomerCreditLimit
		from erpnext.selling.doctype.sales_team.sales_team import SalesTeam
		from erpnext.utilities.doctype.portal_user.portal_user import PortalUser
		from frappe.types import DF

		account_manager: DF.Link | None
		accounts: DF.Table[PartyAccount]
		agent_group: DF.Link | None
		agent_name: DF.Data
		agent_type: DF.Literal["Company", "Individual", "Proprietorship", "Partnership"]
		companies: DF.Table[AllowedToTransactWith]
		credit_limits: DF.Table[CustomerCreditLimit]
		customer_details: DF.Text | None
		customer_pos_id: DF.Data | None
		customer_primary_address: DF.Link | None
		customer_primary_contact: DF.Link | None
		default_bank_account: DF.Link | None
		default_commission_rate: DF.Float
		default_currency: DF.Link | None
		default_price_list: DF.Link | None
		default_sales_partner: DF.Link | None
		disabled: DF.Check
		dn_required: DF.Check
		email_id: DF.ReadOnly | None
		gender: DF.Link | None
		image: DF.AttachImage | None
		industry: DF.Link | None
		is_frozen: DF.Check
		is_internal_customer: DF.Check
		language: DF.Link | None
		loyalty_program: DF.Link | None
		loyalty_program_tier: DF.Data | None
		market_segment: DF.Link | None
		mobile_no: DF.ReadOnly | None
		mode_of_payment: DF.Link | None
		payment_terms: DF.Link | None
		portal_users: DF.Table[PortalUser]
		primary_address: DF.Text | None
		represents_company: DF.Link | None
		sales_team: DF.Table[SalesTeam]
		so_required: DF.Check
		tax_category: DF.Link | None
		tax_id: DF.Data | None
		tax_withholding_category: DF.Link | None
		territory: DF.Link | None
		website: DF.Data | None
	# end: auto-generated types
	pass
	def validate(self):
		self.add_role_for_user()

	def onload(self):
		self.load_dashboard_info()
		
	def add_role_for_user(self):
		for portal_user in self.portal_users:
			add_role_for_portal_user(portal_user, "Agent User")


	def load_dashboard_info(self):
		info = get_dashboard_info(self.doctype, self.name, self.loyalty_program)
		self.set_onload("dashboard_info", info)