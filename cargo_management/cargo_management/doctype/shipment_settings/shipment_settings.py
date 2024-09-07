# Copyright (c) 2024, Agile Shift and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ShipmentSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from cargo_management.shipment_management.doctype.shipping_cash_account_group.shipping_cash_account_group import ShippingCashAccountGroup
		from cargo_management.shipment_management.doctype.shipping_expenses_account_group.shipping_expenses_account_group import ShippingExpensesAccountGroup
		from cargo_management.shipment_management.doctype.transport_accounting_dimension.transport_accounting_dimension import TransportAccountingDimension
		from erpnext.accounts.doctype.party_account.party_account import PartyAccount
		from frappe.types import DF

		accounting_dimension: DF.Table[TransportAccountingDimension]
		accounts: DF.Table[PartyAccount]
		advance_accounts: DF.Table[PartyAccount]
		barcode_type: DF.Literal["", "EAN", "EAN-8", "EAN-12", "UPC-A", "UPC-E", "CODE-39", "GS1", "GTIN", "ISBN", "ISBN-10", "ISBN-13", "ISSN", "JAN", "PZN"]
		cash_or_bank_account_group: DF.TableMultiSelect[ShippingCashAccountGroup]
		create_invoice: DF.Literal["Manually", "Automatically"]
		default_commission_rate: DF.Float
		default_sales_item: DF.Link | None
		expense_account_group: DF.TableMultiSelect[ShippingExpensesAccountGroup]
		fuel_item: DF.Link
		fuel_item_group: DF.Link | None
		is_submit: DF.Check
		sales_item_group: DF.Link | None
		vehicle_fuel_parent_warehouse: DF.Link | None
	# end: auto-generated types
	pass
