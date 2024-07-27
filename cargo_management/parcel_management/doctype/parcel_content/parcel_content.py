from frappe.model.document import Document


class ParcelContent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_weight: DF.Float
		amount: DF.Currency
		description: DF.SmallText
		height: DF.Int
		import_rate: DF.Float
		item_code: DF.Link | None
		length: DF.Int
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
