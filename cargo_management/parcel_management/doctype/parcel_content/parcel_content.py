from frappe.model.document import Document


class ParcelContent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_weight: DF.Float
		amount: DF.Currency
		color: DF.Link | None
		description: DF.SmallText | None
		height: DF.Int
		import_rate: DF.Float
		invoice: DF.Link | None
		item_code: DF.Link | None
		length: DF.Int
		net_amount: DF.Currency
		net_rate: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Int
		rate: DF.Currency
		shipping_rule: DF.Link | None
		tracking_number: DF.Data | None
		volumetric_weight: DF.Float
		weight_type: DF.Literal["Actual Weight", "Volumetric Weight"]
		width: DF.Int
	# end: auto-generated types
	pass
