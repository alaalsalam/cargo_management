# Copyright (c) 2024, Agile Shift and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ShippingAccountingDimension(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		child_field_name: DF.Data | None
		dimension_name: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		source_doctype: DF.Link
		source_field_name: DF.Data | None
		source_type: DF.Literal["Field", "Value", "Child"]
		target_child_field_name: DF.Data | None
		target_doctype: DF.Link
		target_field_name: DF.Data | None
		target_type: DF.Literal["Main", "Child"]
		value: DF.Data | None
	# end: auto-generated types
	pass
