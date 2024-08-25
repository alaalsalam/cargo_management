from easypost.errors.api import ApiError as EasyPostAPIError

import frappe
from frappe import _
from frappe.model.document import Document
from .api.api_17track import API17Track
from .api.easypost_api import EasyPostAPI
from .constants import Status, StatusMessage
from .utils import ParcelStateMachine
from frappe.utils import nowdate, cstr, cint, flt, comma_or, now
import json

import random
import string

class Parcel(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from cargo_management.parcel_management.doctype.parcel_content.parcel_content import ParcelContent
		from frappe.types import DF

		agent: DF.Link
		amended_from: DF.Link | None
		barcode: DF.Barcode | None
		cargo_shipment: DF.Link | None
		carrier: DF.Literal["Drop Off", "Pick Up", "Unknown", "Amazon", "USPS", "UPS", "DHL", "FedEx", "OnTrac", "Cainiao", "SF Express", "Yanwen", "YunExpress", "SunYou", "Pitney Bowes", "Veho"]
		carrier_est_delivery: DF.Datetime | None
		carrier_est_weight: DF.Float
		carrier_last_detail: DF.SmallText | None
		carrier_real_delivery: DF.Datetime | None
		carrier_status: DF.Literal["Unknown", "Pre Transit", "In Transit", "Out For Delivery", "Available For Pickup", "Delivered", "Return To Sender", "Failure", "Cancelled", "Error"]
		carrier_status_detail: DF.Data | None
		company: DF.Link
		content: DF.Table[ParcelContent]
		currency: DF.Link | None
		destination: DF.Data | None
		easypost_id: DF.Data | None
		est_delivery_1: DF.Date | None
		est_delivery_2: DF.Date | None
		est_departure: DF.Date | None
		explained_status: DF.Data | None
		has_taxes: DF.Check
		mode_of_payment: DF.Link | None
		naming_series: DF.Literal["UN"]
		net_total: DF.Currency
		notes: DF.SmallText | None
		order_date: DF.Date | None
		parcel_price_rule: DF.Link | None
		piece_type: DF.Literal["Box", "Envelope", "Pallet", "Carton", "Luggage", "Crate", "Others"]
		receiver_address: DF.Data | None
		receiver_email: DF.Data | None
		receiver_name: DF.Link | None
		receiver_number: DF.Data | None
		receivers_card_image: DF.Attach | None
		shipper: DF.Link | None
		shipper_address: DF.Data | None
		shipper_card_image: DF.Attach | None
		shipper_email: DF.Data | None
		shipper_name: DF.Link | None
		shipper_number: DF.Data | None
		shipping_amount: DF.Currency
		signed_by: DF.Data | None
		status: DF.Literal["Awaiting Receipt", "Awaiting Confirmation", "In Extraordinary Confirmation", "Awaiting Departure", "In Transit", "In Customs", "Sorting", "To Bill", "Unpaid", "For Delivery or Pickup", "Finished", "Cancelled", "Never Arrived", "Returned to Sender"]
		total: DF.Currency
		total_actual_weight: DF.Float
		total_net_height: DF.Float
		total_net_length: DF.Float
		total_net_width: DF.Float
		total_qty: DF.Int
		total_volumetric_weight: DF.Float
		tracking_number: DF.Data | None
		transportation: DF.Literal["Sea", "Air"]
		warehouse_receipt: DF.Link | None
		weight_type: DF.Literal["Actual Weight", "Volumetric Weight"]
	# end: auto-generated types
	"""  All these are Frappe Core Flags:
		'ignore_links':       avoid: _validate_links()
		'ignore_validate':    avoid: validate() and before_save()
		'ignore_mandatory':   avoid: _validate_mandatory()
		'ignore_permissions': avoid: will not check for permissions globally.
	"""

	# TODO: Add Override Decorator for python 3.12
	# TODO: Replace frappe.get_doc for DoctypeClass import. for Typing Completion

	# ----------------------- Ala Added
	@frappe.whitelist()
	def apply_parcel_price_rule(self):
		if self.parcel_price_rule:
			parcel_price_rule = frappe.get_doc("Parcel Price Rule", self.parcel_price_rule)
			parcel_price_rule.apply(self)

			# self.calculate_taxes_and_totals()
   
	def get_shipping_address(self):
		"""Returns Address object from shipping address fields if present"""

		# shipping address fields can be `shipping_address_name` or `shipping_address`
		# try getting value from both

		for fieldname in ("shipping_address_name", "shipping_address"):
			shipping_field = self.meta.get_field(fieldname)
			if shipping_field and shipping_field.fieldtype == "Link":
				if self.get(fieldname):
					return frappe.get_doc("Address", self.get(fieldname))

		return {}
   # --------------------------------------
	#@override
	def save(self, *args, **kwargs):
		""" Override def to change validation behaviour. Useful when called from outside a form. """

		return super(Parcel, self).save(*args, **kwargs)

	def validate(self):
		self.apply_parcel_price_rule()
		""" Sanitize fields """
		self.tracking_number = self.name
		self.tracking_number = self.tracking_number.strip().upper()  # Only uppercase with no spaces
		for tracking in self.content:
			tracking.tracking_number = str(self.tracking_number) + "-" + str(tracking.idx)
			
	def before_save(self):
		""" Before saved in DB and after validated. Add new data. This runs on Insert(Create) or Save(Update)"""

		if self.is_new():
			self.get_generated_barcode()
		elif self.has_value_changed('shipper') or self.has_value_changed('tracking_number'):  # Exists and data has changed
			frappe.msgprint("Shipper or Tracking Number has changed, we have requested new data.", indicator='yellow', alert=True)

	def change_status(self, new_status):
		"""
		Validates the current status of the parcel and change it if it's possible.

		# Parcel was waiting for receipt, now is mark as delivered. waiting for confirmation.
		# Parcel was waiting for receipt or confirmation and now is waiting for the departure.
		# Parcel was not received and not confirmed, but has appear on the warehouse receipt.

		# TODO: Validate this when status is changed on Form-View or List-View
		"""
		# psm = ParcelStateMachine(status=self.status)
		# psm.transition(new_status)

		if (self.status != new_status and \
			(self.status == 'Awaiting Receipt' and new_status in ['Awaiting Confirmation', 'Returned to Sender']) or \
			(self.status in ['Awaiting Receipt', 'Awaiting Confirmation', 'In Extraordinary Confirmation', 'Cancelled'] and new_status == 'Awaiting Departure') or \
			(self.status == 'Awaiting Departure' and new_status == 'In Transit') or \
			(self.status in ['Awaiting Receipt', 'Awaiting Confirmation', 'In Extraordinary Confirmation', 'Awaiting Departure', 'In Transit', 'Cancelled'] and new_status == 'Sorting') or \
			(self.status not in ['Unpaid', 'For Delivery or Pickup', 'Finished'] and new_status == 'To Bill') or \
			(self.status in ['Sorting', 'To Bill'] and new_status == 'Unpaid') or \
			(self.status == 'Unpaid' and new_status == 'For Delivery or Pickup')):
			self.status = new_status
			return True

		return False

	def get_generated_barcode(self):
		"""
		Fetch the barcode type from the Shipment Settings doctype and generate a barcode based on the type.
		"""
		shipment_settings = frappe.get_doc("Shipment Settings")
		barcode_type = shipment_settings.barcode_type
		self.barcode = generate_barcode(barcode_type)

	@property
	def explained_status(self):
		""" This returns a detailed explanation of the current status of the Parcel and compatible colors. """
		# TODO: Python 3.10: Migrate to switch case or Improve performance?
		# frappe.local.lang = LocaleLanguage.SPANISH  # Little Hack

		message, color = [], 'blue'  # TODO: Add more colors? Check frappe colors

		match self.status:
			case Status.AWAITING_RECEIPT:
				message = [StatusMessage.TRANSPORTATION_NOT_DELIVERED_YET]

				if self.carrier_est_delivery:  # The carrier has provided an estimated delivery date
					est_delivery_diff = frappe.utils.date_diff(None, self.carrier_est_delivery)  # Diff from estimated to today
					est_delivery_date = frappe.utils.format_date(self.carrier_est_delivery, 'medium')  # readable date

					if est_delivery_diff == 0:  # Delivery is today
						message.append(StatusMessage.ESTIMATED_DELIVERY_DATE_TODAY)
					elif est_delivery_diff == -1:  # Delivery is tomorrow
						message.append(StatusMessage.ESTIMATED_DELIVERY_DATE_TOMORROW)
					elif est_delivery_diff < 0:  # Delivery is in the next days
						# message.append('La fecha programada es: {}'.format(est_delivery_date))
						message.append(StatusMessage.ESTIMATED_DELIVERY_DATE.value.replace('[DATE]', est_delivery_date))
					else:  # Delivery is late
						color = 'pink'
						# message.append('Esta retrasado. Debio de ser entregado el: {}'.format(est_delivery_date))
						message.append(StatusMessage.DELAYED_DELIVERY_DATE.value.replace('[DATE]', est_delivery_date))
						message.append(StatusMessage.CONTACT_YOUR_PROVIDER_FOR_INFO)
				else:
					color = 'yellow'
					message.append(StatusMessage.NOT_DELIVERY_DATE_ESTIMATED)

			case Status.AWAITING_CONFIRMATION:
				message, color = self._awaiting_confirmation_or_in_extraordinary_confirmation()
			case Status.IN_EXTRAORDINARY_CONFIRMATION:
				message, color = self._awaiting_confirmation_or_in_extraordinary_confirmation()
			case Status.AWAITING_DEPARTURE:
				# TODO: Add Warehouse Receipt date, # TODO: Add cargo shipment calendar
				# cargo_shipment = frappe.get_cached_doc('Cargo Shipment', self.cargo_shipment)

				# TODO: What if we dont have real delivery date. Or signature
				message = [
					StatusMessage.TRANSPORTER_DELIVERY_DATE.value.replace(
						'[DATE]',
						frappe.utils.format_datetime(self.carrier_real_delivery, 'medium')
					),
					# 'Firmado por {}'.format(self.carrier_real_delivery, self.signed_by),
					# 'Fecha esperada de recepcion en Managua: {}'.format(cargo_shipment.expected_arrival_date),

					# 'Embarque: {}'.format(self.cargo_shipment)
				]
				if self.signed_by:
					message.append(StatusMessage.SIGNED_BY.value.replace('[SIGNER]', str(self.signed_by)))

			case Status.IN_TRANSIT:
				# TODO: Add Departure date and est arrival date
				if not self.cargo_shipment:
					return {'message': [StatusMessage.NO_CARGO_SHIPPING], color: 'red'}

				cargo_shipment = frappe.get_cached_doc('Cargo Shipment', self.cargo_shipment)

				color = 'purple'

				message = [
					StatusMessage.PACKAGE_IN_TRANSIT_TO_DESTINATION,
					StatusMessage.DEPARTURE_DATE.value.replace('[DATE]', str(cargo_shipment.departure_date)),
					StatusMessage.ESTIMATED_RECEPTION_DATE.value.replace('[DATE]', str(cargo_shipment.expected_arrival_date)),
					StatusMessage.CARGO_SHIPMENT.value.replace('[SHIPMENT]', self.cargo_shipment)
				]
			case Status.IN_CUSTOMS:
				message, color = [StatusMessage.PACKAGE_IN_CUSTOMS], 'gray'
			case Status.SORTING:
				message, color = [StatusMessage.PACKAGE_IN_OFFICE_SORTING], 'blue'
			case Status.TO_BILL:
				message, color = [StatusMessage.PACKAGE_IN_OFFICE_SORTING], 'blue'

			case Status.UNPAID:
				message, color = [StatusMessage.PACKAGE_READY], 'blue'
			case  Status.FOR_DELIVERY_OR_PICKUP:
				message, color = [StatusMessage.PACKAGE_READY], 'blue'

			case Status.FINISHED:
				message, color = [StatusMessage.PACKAGE_FINISHED], 'green'  # TODO: Show invoice, delivery and payment details.
			case Status.CANCELLED:
				message, color = [StatusMessage.CONTACT_AGENT_FOR_PACKAGE_INFO], 'orange'
			case Status.NEVER_ARRIVED:
				message, color = [StatusMessage.PACKAGE_NEVER_ARRIVED], 'red'
				message.append(StatusMessage.CONTACT_FOR_MORE_INFO)
			case Status.RETURNED_TO_SENDER:
				message, color = [StatusMessage.PACKAGE_RETURNED], 'red'
				message.append(StatusMessage.CONTACT_FOR_MORE_INFO)

			case _:
				...

		return {'message': message, 'color': color}



	# def update_from_api_data(self, api_data: dict) -> None:
	# 	""" This updates the parcel with the data from the API. """
	# 	print(api_data)
	# 	self.__dict__.update(api_data)  # Updating all the DICT to the Parcel DocType

	# 	if api_data['carrier_status'] == 'Delivered':  # or api_data['carrier_status_detail'] == 'Arrived At Destination':
	# 		self.change_status('Awaiting Confirmation')
	# 	elif api_data['carrier_status'] == 'Return To Sender' or self.carrier_status_detail == 'Return':
	# 		self.change_status('Returned to Sender')
	# 	else:  # TODO: Change the status when the carrier status: failure, cancelled, error
	# 		self.change_status('Awaiting Receipt')

	def _awaiting_confirmation_or_in_extraordinary_confirmation(self):
		if self.carrier_real_delivery:
			color = 'blue'
			message = [StatusMessage.TRANSPORTATION_DELIVERED_DATE.value.replace('[DATE]', frappe.utils.format_datetime(self.carrier_real_delivery,"EEEE, d 'de' MMMM yyyy 'a las' h:mm a").capitalize())]

			if self.signed_by:
				message.append(StatusMessage.SIGNED_BY.value.replace('[SIGNER]', self.signed_by))

				# TODO: check against current user tz: Change None to now in local delivery place timezone
				delivered_since = frappe.utils.time_diff(None, self.carrier_real_delivery)  # datetime is UTC

				# TODO: Compare Against Workable days
				# Parcel has exceeded the 24 hours timespan to be confirmed. Same as: time_diff_in_hours() >= 24.00
				if delivered_since.days >= 1:  # The day starts counting after 1-minute difference
					color = 'red'
					delivered_since_str = StatusMessage.HAS_BEEN_1_DAY if delivered_since.days == 1 else StatusMessage.HAS_BEEN_X_DAYS

					message.append(delivered_since_str.value.replace('[DAYS]', str(delivered_since.days)))
				else:
					message.append(StatusMessage.WAIT_FOR_24_HOURS_CONFIRMATION)

		if self.carrier_est_delivery:
			color = 'yellow'
			message = [StatusMessage.TRANSPORTER_INDICATE_ESTIMATE_DELIVERY_DATE.value.replace('[DATE]', frappe.utils.format_datetime(self.carrier_est_delivery,'medium'))]
		else:
			color = 'yellow'
			message = [StatusMessage.NOT_DELIVERY_DATE_ESTIMATED, StatusMessage.CONTACT_FOR_MORE_INFO]

		if self.status == Status.IN_EXTRAORDINARY_CONFIRMATION:
			color = 'pink'
			message.append(StatusMessage.PACKAGE_IN_EXTRAORDINARY_REVISION)

		return message, color


@frappe.whitelist()
def create_sales_invoice(doc, rows):
		doc = frappe.get_doc(json.loads(doc))
		rows = json.loads(rows)
		
		if not rows:
			return
		# if not doc.currency:
		# 		doc.currency = frappe.defaults.get_user_default("currency")  # Set default currency if not provided

		items = []
		item_row_per = []

		for row in rows:
			item = frappe._dict({
				"item_code": row["item_code"],
				"qty": 1,
				"uom": frappe.get_value("Item", row["item_code"], "stock_uom"),
				"package": doc.get("name"),
				"rate": row["rate"],
				"description": row["description"],
			})
			item_row_per.append([row, item])
			items.append(item)
		
		invoice = frappe.get_doc({
			"doctype": "Sales Invoice",
			"customer": doc.shipper_name,
			"currency": doc.currency,
			"posting_date": nowdate(),
			"company": doc.company,
			"items": items,
		})

		frappe.flags.ignore_account_permission = True
		invoice.set_taxes()
		invoice.set_missing_values()
		invoice.flags.ignore_mandatory = True
		invoice.calculate_taxes_and_totals()
		invoice.insert(ignore_permissions=True)

		for item in doc.content:
			if item.name in [i["name"] for i in rows]:
				item.invoice = invoice.name
    
		doc.save()

		frappe.msgprint(_("Sales Invoice {0} Created").format(invoice.name), alert=True)
		return invoice


# -------------------------------------------------------------------------
def generate_barcode(barcode_type):
    """
    Generate a barcode based on the given barcode type.
    """
    barcode = ''

    if barcode_type == 'EAN':
        barcode = str(random.randint(1000000000000, 9999999999999))
    elif barcode_type == 'UPC-A':
        barcode = str(random.randint(100000000000, 999999999999))
    elif barcode_type == 'CODE-39':
        barcode = 'C39-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
    elif barcode_type == 'EAN-12':
        barcode = str(random.randint(100000000000, 999999999999))
    elif barcode_type == 'EAN-8':
        barcode = str(random.randint(10000000, 99999999))
    elif barcode_type in ('GS1', 'GTIN'):
        barcode = str(random.randint(1000000000000, 9999999999999))
    elif barcode_type == 'ISBN-10':
        barcode = str(random.randint(100000000, 999999999))
        check_digit_10 = calculate_isbn_10_check_digit(barcode)
        barcode += str(check_digit_10)
    elif barcode_type in ('ISBN-13', 'ISBN'):
        barcode = '978' + str(random.randint(100000000000, 999999999999))[3:]
        check_digit_13 = calculate_isbn_13_check_digit(barcode)
        barcode += str(check_digit_13)
    elif barcode_type == 'ISSN':
        barcode = str(random.randint(10000000, 99999999))
    elif barcode_type == 'JAN':
        barcode = str(random.randint(100000000000, 999999999999))
    elif barcode_type == 'PZN':
        barcode = 'PZN-' + str(random.randint(1000000, 9999999))
    elif barcode_type == 'UPC':
        barcode = str(random.randint(100000000000, 999999999999))
    else:
        print(f'Unknown barcode type: {barcode_type}')
        barcode = 'CR-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))

    return barcode

def calculate_isbn_10_check_digit(isbn_10):
    """
    Calculate the check digit for an ISBN-10 barcode.
    """
    total = sum(int(digit) * (10 - i) for i, digit in enumerate(isbn_10))
    check_digit = total % 11
    return 'X' if check_digit == 10 else check_digit

def calculate_isbn_13_check_digit(isbn_13):
    """
    Calculate the check digit for an ISBN-13 barcode.
    """
    total = sum(int(digit) * (1 if i % 2 == 0 else 3) for i, digit in enumerate(isbn_13))
    check_digit = 10 - (total % 10)
    return check_digit if check_digit != 10 else 0
