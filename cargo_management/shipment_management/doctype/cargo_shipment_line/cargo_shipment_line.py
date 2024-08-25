from frappe.model.document import Document


class CargoShipmentLine(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_weight: DF.Float
		carrier: DF.Literal["Amazon", "USPS", "UPS", "FedEx", "DHL", "LaserShip", "Drop Off", "Pick Up"]
		carrier_est_weight: DF.Float
		carrier_real_delivery: DF.Datetime | None
		comments: DF.SmallText | None
		customer: DF.Link | None
		customer_name: DF.Data | None
		description: DF.SmallText | None
		destination: DF.Data | None
		height: DF.Float
		invoice: DF.Link | None
		item: DF.Link | None
		length: DF.Float
		net_total: DF.Currency
		package: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		received_date: DF.Date | None
		receiver_name: DF.Data | None
		receiver_number: DF.Data | None
		shipping_amount: DF.Currency
		total: DF.Currency
		total_qty: DF.Int
		transportation: DF.Literal["Air", "Sea"]
		type: DF.Literal["Box", "Envelope", "Pallet"]
		volumetric_weight: DF.Float
		warehouse_est_weight: DF.Float
		warehouse_receipt: DF.Link | None
		width: DF.Float
	# end: auto-generated types
	pass
