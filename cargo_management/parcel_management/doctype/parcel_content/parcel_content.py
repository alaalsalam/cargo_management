from frappe.model.document import Document


class ParcelContent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_weight: DF.Float
		amount: DF.Currency
		color: DF.Literal["", "\u0627\u0628\u064a\u0636", "\u0627\u0633\u0648\u062f", "\u0627\u062d\u0645\u0631", "\u0627\u0635\u0641\u0631", "\u0627\u062e\u0636\u0631", "\u0627\u0632\u0631\u0642", "\u0628\u0646\u064a", "\u062e\u0634\u0628\u064a"]
		description: DF.SmallText
		height: DF.Int
		import_rate: DF.Float
		invoice: DF.Link | None
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
