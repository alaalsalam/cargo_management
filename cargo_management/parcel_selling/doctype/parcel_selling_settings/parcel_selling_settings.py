# Copyright (c) 2022, Agile Shift and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ParcelSellingSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		air_departure_days: DF.Data | None
		sea_departure_days: DF.Data | None
		transit_days_air_1: DF.Int
		transit_days_air_2: DF.Int
		transit_days_sea_1: DF.Int
		transit_days_sea_2: DF.Int
	# end: auto-generated types
	pass
