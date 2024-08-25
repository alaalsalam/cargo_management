from frappe.model.document import Document


class CargoPackingList(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from cargo_management.shipment_management.doctype.cargo_packing_list_line.cargo_packing_list_line import CargoPackingListLine
		from frappe.types import DF

		cargo_shipment: DF.Link
		content: DF.Table[CargoPackingListLine]
	# end: auto-generated types
	pass
