import frappe
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
from erpnext.controllers.accounts_controller import (
	AccountsController,
	get_supplier_block_status,
	validate_taxes_and_charges,
)
from erpnext.accounts.utils import (
	cancel_exchange_gain_loss_journal,
	get_account_currency,
	get_balance_on,
	get_outstanding_invoices,
	get_party_types_from_account_type,
)
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry

class WarehouseReceipt(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from cargo_management.warehouse_management.doctype.warehouse_receipt_line.warehouse_receipt_line import WarehouseReceiptLine
		from frappe.types import DF

		agent: DF.Link
		agent_account: DF.Link | None
		amended_from: DF.Link | None
		carrier_est_gross_weight: DF.Float
		company: DF.Link
		cost_center: DF.Link | None
		departure_date: DF.Date | None
		description: DF.SmallText | None
		mode_of_payment: DF.Link | None
		naming_series: DF.Literal["SHIP-WAR-.YYYY.-"]
		paid_amount: DF.Currency
		paid_from_account_balance: DF.Currency
		paid_from_account_currency: DF.Link | None
		paid_to: DF.Link | None
		paid_to_account_balance: DF.Currency
		paid_to_account_currency: DF.Link | None
		party_balance: DF.Currency
		posting_date: DF.Date | None
		received_amount: DF.Currency
		source_exchange_rate: DF.Float
		status: DF.Literal["Draft", "Open", "Awaiting Departure", "In Transit", "Sorting", "Finished"]
		target_exchange_rate: DF.Float
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

	
	
	@frappe.whitelist()
	def calculate_total_amount(doc):
		total_amount = sum(row.get("shipping_amount", 0) for row in doc.get("warehouse_receipt_lines", []))
		# frappe.msgprint(f"Total Amount: {total_amount}")
		return total_amount

	
	def build_gl_map(self):
			gl_entries = []
			self.add_bank_gl_entries(gl_entries)
			return gl_entries

	def make_gl_entries(self, cancel=0, adv_adj=0):
			gl_entries = self.build_gl_map()
			# gl_entries = process_gl_map(gl_entries)
			make_gl_entries(gl_entries, cancel=cancel, adv_adj=adv_adj)
			if cancel:
				cancel_exchange_gain_loss_journal(frappe._dict(doctype=self.doctype, name=self.name))
			else:
				self.make_exchange_gain_loss_journal()

			self.make_advance_gl_entries(cancel=cancel)


	def make_advance_gl_entries(
			self, entry: object | dict = None, cancel: bool = 0, update_outstanding: str = "Yes"
		):
			gl_entries = []
			if cancel:
				make_reverse_gl_entries(gl_entries, partial_cancel=True)
			else:
				make_gl_entries(gl_entries, update_outstanding=update_outstanding)


	def add_bank_gl_entries(self, gl_entries):
				gl_entries.append(
					self.get_gl_dict(
						{
							"account": self.agent_account,
							"account_currency": self.paid_to_account_currency,
							# "party_type":"Agent",
							# "party":self.agent,
							"against": self.paid_to,
							"credit_in_account_currency": self.paid_amount,
							"credit": self.paid_amount,
							"cost_center": self.cost_center,
						},
						item=self,
					)
				)
				gl_entries.append(
					self.get_gl_dict(
						{
							"account": self.paid_to,
							"account_currency": self.paid_to_account_currency,
							"against": self.agent_account,
							"debit_in_account_currency": self.paid_amount,
							"debit": self.paid_amount,
							"cost_center": self.cost_center,
						},
						item=self,
					)
				)



@frappe.whitelist()
def get_account_for_company(agent, company):
    agent_doc = frappe.get_doc("Agent", agent)
    
    for row in agent_doc.accounts:
        if row.company == company:
            return row.account
    
    frappe.throw(_("No account found for the selected company and agent."))

@frappe.whitelist()
def get_account_for_mode_of_payment(agent, company):
    agent_doc = frappe.get_doc("Mode of Payment", agent)
    
    for row in agent_doc.accounts:
        if row.company == company:
            return row.default_account
    
    frappe.throw(_("No account found for the selected company and agent."))