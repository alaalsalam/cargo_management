import frappe
import erpnext
from frappe import _
from cargo_management.utils import get_list_from_child_table
from frappe.model.document import Document

from erpnext.accounts.general_ledger import (
	make_gl_entries,
	make_reverse_gl_entries,
	process_gl_map,
)
from erpnext.accounts.utils import (
	create_gain_loss_journal,
	get_account_currency,
	get_currency_precision,
	get_fiscal_years,
	validate_fiscal_year,
)
from frappe.utils import cint, comma_or, flt, getdate, nowdate
from erpnext.accounts.utils import (
	cancel_exchange_gain_loss_journal,
	get_account_currency,
	get_balance_on,
	get_outstanding_invoices,
	get_party_types_from_account_type,
)
from erpnext.accounts.party import get_party_account

from erpnext.accounts.doctype.bank_account.bank_account import (
	get_bank_account_details,
	get_default_company_bank_account,
	get_party_bank_account,
)
from erpnext.accounts.doctype.invoice_discounting.invoice_discounting import (
	get_party_account_based_on_invoice_discounting,
)
from erpnext.controllers.accounts_controller import AccountsController

class WarehouseReceipt(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from cargo_management.warehouse_management.doctype.warehouse_receipt_line.warehouse_receipt_line import WarehouseReceiptLine
		from frappe.types import DF

		agent: DF.Link
		agent_account: DF.Link
		amended_from: DF.Link | None
		carrier_est_gross_weight: DF.Float
		commission_rate: DF.Float
		company: DF.Link
		cost_center: DF.Link | None
		departure_date: DF.Date | None
		description: DF.SmallText | None
		mode_of_payment: DF.Link | None
		naming_series: DF.Literal["SHIP-WAR-.YYYY.-"]
		paid_from_account_balance: DF.Currency
		paid_from_account_currency: DF.Link | None
		paid_to: DF.Link
		paid_to_account_balance: DF.Currency
		paid_to_account_currency: DF.Link | None
		party_balance: DF.Currency
		posting_date: DF.Date
		received_amount: DF.Currency
		source_exchange_rate: DF.Float
		status: DF.Literal["Draft", "Open", "Awaiting Departure", "In Transit", "Sorting", "Finished"]
		target_exchange_rate: DF.Float
		total_commission: DF.Currency
		total_shipment_amount: DF.Currency
		total_shipping_price: DF.Float
		transportation: DF.Literal["", "Sea", "Air"]
		volumetric_weight: DF.Float
		warehouse_est_gross_weight: DF.Float
		warehouse_receipt_lines: DF.Table[WarehouseReceiptLine]
	# end: auto-generated types
		# begin: auto-generated types
		# This code is auto-generated. Do not modify anything in this block.


	def on_update(self):
		""" Add Warehouse Receipt Link to the Package. This allows to have mutual reference WR to Package. """
		# FIXME: If Warehouse Receipt is deleted, remove link from Package
		# TODO: Add extra fields from Warehouse Receipt -> Receipt Date & Weight

		# We only change the warehouse_receipt field if it is different from current.
		packages = get_list_from_child_table(self.warehouse_receipt_lines, 'parcel')

		if not packages:
			return
		if self.name:
			frappe.db.sql("""
			UPDATE tabParcel
			SET warehouse_receipt = %(wr_name)s
			WHERE name IN %(packages)s AND COALESCE(warehouse_receipt, '') != %(wr_name)s
			""", {
				'wr_name': self.name,
				'packages': packages
			})

	# TODO: Actually change the status after the package is validated and creadted. maybe at status change from draft to open?

	def change_status(self, new_status):
		""" Validates the current status of the warehouse receipt and change it if it's possible. """

		# TODO: Validate this when status is changed on Form-View or List-View

		# TODO: FINISH
		if self.status != new_status and \
			(self.status == 'Open' and new_status == 'Awaiting Departure') or \
			(self.status in ['Open', 'Awaiting Departure'] and new_status == 'In Transit') or \
			(self.status in ['Open', 'Awaiting Departure', 'In Transit'] and new_status == 'Sorting') or \
			(self.status in ['Open', 'Awaiting Departure', 'In Transit', 'Sorting'] and new_status == 'Finished'):
			self.status = new_status
			return True

		return False
	def validate(self):
		pass


	def on_submit(self):
		self.make_gl_entries()

	
	
	# @frappe.whitelist()
	# def calculate_total_amount(doc):
	# 		total_amount = sum(row.get("shipping_amount", 0) for row in doc.get("warehouse_receipt_lines", [])) 
	# 		return total_amount




	def make_gl_entries(self, gl_entries=None, from_repost=False):
		from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries
		if not gl_entries:
			gl_entries = self.get_gl_entries()

		if gl_entries:

			if self.docstatus == 1:
				make_gl_entries(
					gl_entries,
					merge_entries=False,
					from_repost=from_repost,
				)
		
			# from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt

			# update_outstanding_amt(
			# 	self.debit_to,
			# 	"Customer",
			# 	self.customer,
			# 	self.doctype,
			# 	self.return_against if cint(self.is_return) and self.return_against else self.name,
			# )


 
	def get_gl_entries(self, warehouse_account=None):
		from erpnext.accounts.general_ledger import merge_similar_entries

		gl_entries = []

		self.make_agent_gl_entry(gl_entries)
		self.make_parcel_gl_entries(gl_entries)


		return gl_entries

	def make_agent_gl_entry(self, gl_entries):
		if self.commission_rate:
			shipping_amount_after_commission = self.total_shipment_amount - self.total_commission
		else:
			shipping_amount_after_commission = self.total_shipment_amount
		gl_entries.append(
			self.get_gl_dict(
				{
					"account": self.agent_account,
					"party_type": "Agent",
					"party": self.agent,
					"posting_date": self.posting_date,
					"against": self.paid_to,
					"debit": shipping_amount_after_commission,
					"debit_in_account_currency": shipping_amount_after_commission,
					"against_voucher": self.name,
					"against_voucher_type": self.doctype,
					"cost_center": self.cost_center,
					# "project": self.project,
				},
				item=self,
			)
		)
		if self.total_commission:
			gl_entries.append(
					self.get_gl_dict(
						{
							"account": self.paid_to,
							"posting_date": self.posting_date,
							"against": self.agent_account,
							"debit": self.total_commission,
							"debit_in_account_currency": self.total_commission,
							# "against_voucher": self.name,
							# "against_voucher_type": self.doctype,
							"cost_center": self.cost_center,
							# "project": self.project,
						},
						item=self,
					)
				)

	def make_parcel_gl_entries(self, gl_entries):
		for item in self.get("warehouse_receipt_lines"):
			if item.shipping_amount:
				income_account = self.paid_to
				account_currency = get_account_currency(income_account)
				gl_entries.append(
					self.get_gl_dict(
						{
							"account": income_account,
							"against": self.agent,
							"credit": flt(item.shipping_amount, item.precision("shipping_amount")),
							"credit_in_account_currency": flt(item.shipping_amount, item.precision("shipping_amount")),
							"parcel": item.parcel,
						},
						account_currency,
						item=item,
					)
				)

	# def make_parcel_gl_entries(self, gl_entries):
	# 	for item in self.get("warehouse_receipt_lines"):
	# 		if item.shipping_amount:
	# 			# income_account = item.income_account
	# 			income_account = self.paid_to
	
	# 			# amount, base_amount = self.get_amount_and_base_amount(item, 1)

	# 			account_currency = get_account_currency(income_account)
	# 			gl_entries.append(
	# 				self.get_gl_dict(
	# 					{
	# 						"account": income_account,
	# 						"against": self.agent,
	# 						"credit": flt(item.shipping_amount, item.precision("shipping_amount")),
	# 						"credit_in_account_currency": flt(item.shipping_amount, item.precision("shipping_amount")),
	# 						"parcel": item.parcel,
	# 						# "cost_center": item.cost_center,
	# 						# "project": item.project or self.project,
	# 						# "project": item.project or self.project,
	# 					},
	# 					account_currency,
	# 					item=item,
	# 				)
	# 			)

	# expense account gl entries
	# if cint(self.update_stock) and erpnext.is_perpetual_inventory_enabled(self.company):
	# 	gl_entries += super().get_gl_entries()




@frappe.whitelist()
def get_account_for_company(agent, company, docname=None):
    # Get the agent document
    agent_doc = frappe.get_doc("Agent", agent)
    
    # Check in the agent's accounts
    for row in agent_doc.accounts:
        if row.company == company:
            return row.account
    
    if agent_doc.agent_group:
        agent_group_doc = frappe.get_doc("Agent Group", agent_doc.agent_group)
        
        for row in agent_group_doc.accounts:
            if row.company == company:
                return row.account
    
    settings_doc = frappe.get_single("Shipment Settings")  # Replace "Settings" with your actual settings doctype name
    if settings_doc:
        for row in settings_doc.accounts:  # Replace 'default_accounts' with the appropriate field
            if row.company == company:
                return row.account
    
    frappe.msgprint(_("No account found for the selected company, agent, or agent group. Please choose one."))
    return None

@frappe.whitelist()
def get_rate_for_agent(agent):
    agent_doc = frappe.get_doc("Agent", agent)
    
    agent_rate = agent_doc.get("commission_rate")
    
    if not agent_rate:
        if agent_doc.agent_group:
            agent_group_doc = frappe.get_doc("Agent Group", agent_doc.agent_group)
            agent_rate = agent_group_doc.get("commission_rate")
    
    if not agent_rate:
        agent_rate = frappe.db.get_single_value('Shipment Settings', 'default_commission_rate')
    
    return agent_rate


@frappe.whitelist()
def get_account_for_mode_of_payment(agent, company):
    agent_doc = frappe.get_doc("Mode of Payment", agent)
    
    for row in agent_doc.accounts:
        if row.company == company:
            return row.default_account
    
    frappe.msgprint(_("No account found for the selected company and agent."))

@frappe.whitelist()
def calculate_commission(commission_rate, total):
		if total is None or commission_rate is None:
			return 0.0

		try:
			total = float(total)
			commission_rate = float(commission_rate)
		except ValueError:
			return 0.0
		commission = (total * commission_rate) / 100
		# frappe.msgprint(str(commission))

		return commission


@frappe.whitelist()
def calculate_rate(total, total_commission):
    if total is None or total_commission is None:
        return 0.0

    try:
        total = float(total)
        total_commission = float(total_commission)
    except ValueError:
        return 0.0

    if total == 0:
        return 0.0
    commission_rate = (total_commission / total) * 100
    return commission_rate
