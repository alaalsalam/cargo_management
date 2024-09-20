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
from erpnext.accounts.utils import (
	cancel_exchange_gain_loss_journal,
	get_account_currency,
	get_balance_on,
	get_outstanding_invoices,
)
from erpnext.accounts.general_ledger import (
	make_gl_entries,
	make_reverse_gl_entries,
	process_gl_map,
)
from frappe import _
import random
import string
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.party import get_due_date, get_party_account, get_party_details

class Parcel(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from cargo_management.parcel_management.doctype.parcel_content.parcel_content import ParcelContent
		from frappe.types import DF

		agent: DF.Link
		agent_account: DF.Link
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
		commission_rate: DF.Currency
		company: DF.Link
		content: DF.Table[ParcelContent]
		currency: DF.Link | None
		debit_to: DF.Link | None
		destination: DF.Data | None
		easypost_id: DF.Data | None
		est_delivery_1: DF.Date | None
		est_delivery_2: DF.Date | None
		est_departure: DF.Date | None
		explained_status: DF.Data | None
		has_taxes: DF.Check
		is_parcel_received: DF.Check
		mode_of_payment: DF.Link | None
		naming_series: DF.Literal["UN"]
		net_total: DF.Currency
		not_arrived: DF.Check
		notes: DF.SmallText | None
		order_date: DF.Date | None
		parcel_price_rule: DF.Link | None
		piece_type: DF.Literal["Box", "Envelope", "Pallet", "Carton", "Luggage", "Crate", "Others"]
		receiver_address: DF.Data | None
		receiver_email: DF.Data | None
		receiver_name: DF.Link
		receiver_number: DF.Data | None
		receivers_card_image: DF.Attach | None
		receiving_account: DF.Link | None
		returned_to_sender: DF.Check
		shipper: DF.Link | None
		shipper_address: DF.Data | None
		shipper_card_image: DF.Attach | None
		shipper_email: DF.Data | None
		shipper_name: DF.Link
		shipper_number: DF.Data | None
		shipping_amount: DF.Currency
		signed_by: DF.Data | None
		status: DF.Literal["Awaiting Receipt", "Waiting for Arrival", "Awaiting Confirmation", "In Extraordinary Confirmation", "Awaiting Departure", "In Transit", "In Customs", "Sorting", "To Bill", "Unpaid", "For Delivery or Pickup", "Finished", "Cancelled", "Never Arrived", "Returned to Sender"]
		total: DF.Currency
		total_actual_weight: DF.Float
		total_commission: DF.Currency
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
	@frappe.whitelist()
	def calculate_shipping_amount_by_rule( self,item_code=None, actual_weight=None, length=None ,width=None, height=None):
		pass
		
		# frappe.log(f"Starting calculation with Parcel Price Rule: {self.parcel_price_rule}")

		# if self.parcel_price_rule == 'Volumetric Weight':
		# 	frappe.log("hi - Inside Volumetric Weight condition")
		# 	# if length is not None and width is not None and height is not None:
		# 	# 	try:
		# 	# 		length = float(length)
		# 	# 		width = float(width)
		# 	# 		height = float(height)
					
		# 	# 		volume = length * width * height
					
		# 	# 		if volume < 10:
		# 	# 			return 100
		# 	# 		elif 10 <= volume < 20:
		# 	# 			return 200
		# 	# 		elif 20 <= volume < 30:
		# 	# 			return 300
		# 	# 		else:
		# 	# 			return 400
		# 	# 	except ValueError as e:
		# 	# 		return f"Error: {str(e)}"
		# 	# else:
		# 	# 	return "Error: Length, width, and height are required for volumetric weight calculation."
		
		# elif  self.parcel_price_rule == 'Item Group':
		# 	frappe.log("bye - Inside Item Group condition")

		# 		# item_group = frappe.db.get_value('Item', {'item_code': item_code}, 'item_group')

		# 		# price_rule = frappe.get_all('Parcel Price Rule',
		# 		# 	filters={'item_group': item_group},
		# 		# 	fields=['name']
		# 		# )

		# 		# if price_rule:
		# 		# 	conditions = frappe.get_all('Parcel Rule Condition',
		# 		# 		filters={
		# 		# 			'parent': price_rule[0].name,
		# 		# 			'from_value': ['<=', actual_weight],
		# 		# 			'to_value': ['>=', actual_weight]
		# 		# 		},
		# 		# 		fields=['shipping_amount']
		# 		# 	)

		# 		# 	if conditions:
		# 		# 		shipping_amount = conditions[0].shipping_amount
		# 		# 		frappe.log(f"Shipping Amount: {shipping_amount}")
		# 		# 		return shipping_amount
				
		# 		# frappe.log("No suitable shipping condition found. Returning 0.")
		# 		# return 0
		# else:
		# 	frappe.log("No suitable shipping condition found. Returning 0.")

				# return "Error: Item code and actual weight are required for item group calculation."
		
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

			
# 		self.validate_debit_to_acc()
# 		for child_row in self.get("content"):
#     # الوصول إلى الحقول داخل كل صف في child table
# 			field_item_code = child_row.item_code  # استبدل field_1 باسم الحقل المطلوب
# 			field_actual_weight = child_row.actual_weight

# 			# تمرير الحقول إلى دالة حساب تكلفة الشحن
# 			calculate_shipping_amountb(field_item_code, field_actual_weight)
# # استبدل field_2 باسم الحقل المطلوب
				
				# frappe.log(f"Field 1: {field_1_value}, Field 2: {field_2_value}")		# calculate_shipping_amountb()



		# def before_cancel(self):
	
	# def reverse_gl_entries(self):
	# 	# الحصول على جميع القيود المرتبطة بـ "Parcel"
	# 	gl_entries = frappe.get_all('GL Entry', filters={'voucher_no': self.name})

	# 	for gl_entry in gl_entries:
	# 		gl_doc = frappe.get_doc('GL Entry', gl_entry.name)
			
	# 		# إنشاء قيد عكسي
	# 		reversed_entry = frappe.new_doc('GL Entry')
	# 		reversed_entry.posting_date = gl_doc.posting_date
	# 		reversed_entry.account = gl_doc.account
	# 		reversed_entry.debit = gl_doc.credit  # عكس المدين إلى دائن
	# 		reversed_entry.credit = gl_doc.debit  # عكس الدائن إلى مدين
	# 		reversed_entry.voucher_type = gl_doc.voucher_type
	# 		reversed_entry.voucher_no = gl_doc.voucher_no
	# 		reversed_entry.against = gl_doc.against
	# 		reversed_entry.remarks = "Reversal of GL Entry {0}".format(gl_doc.name)

	# 		# حفظ القيد العكسي
	# 		reversed_entry.insert()
	# 		reversed_entry.submit()

	# 	frappe.msgprint(_("GL Entries have been successfully reversed."))

	# def before_cancel(self):
	# 	# عكس القيود المحاسبية المرتبطة قبل إلغاء "Parcel"
	# 	self.reverse_gl_entries()

	def on_cancel(self):
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Stock Ledger Entry",
			"Payment Ledger Entry",
			"Repost Payment Ledger",
			"Repost Payment Ledger Items",
			"Repost Accounting Ledger",
			"Repost Accounting Ledger Items",
			"Unreconcile Payment",
			"Unreconcile Payment Entries",
		)
		super().on_cancel()
		self.make_gl_entries(cancel=1)

	# هنا تقوم بالإلغاء النهائي للـ Parcel بعد فك الارتباط
		# frappe.db.set(self, 'status', 'Cancelled')
		# frappe.msgprint(_("Parcel has been cancelled successfully."))	
	# def before_save(self):
	# 	auto_create_invoice = frappe.db.get_single_value("Shipment Settings", "create_invoice")

	# 	if auto_create_invoice== "Automatically":
	# 		# الحصول على جميع الصفوف التي لم تُصدر لها فاتورة بعد
	# 		rows = [row for row in self.content if not row.get("invoice")]

	# 		if rows:
	# 			# استدعاء الدالة لإنشاء الفاتورة
	# 			create_sales_invoice(self, json.dumps(rows))
	# 	""" Before saved in DB and after validated. Add new data. This runs on Insert(Create) or Save(Update)"""

	# 	if self.is_new():
	# 		self.get_generated_barcode()
	# 	elif self.has_value_changed('shipper') or self.has_value_changed('tracking_number'):  # Exists and data has changed
	# 
	# 		frappe.msgprint("Shipper or Tracking Number has changed, we have requested new data.", indicator='yellow', alert=True)
	# def before_save(self):
	# 	"""
	# 	Automatically set the status to 'Awaiting Departure' before saving the document.
	# 	"""
	# 	if self.status != 'Awaiting Departure':
	# 		self.status = 'Awaiting Departure'

	

	def change_status(self, new_status):
		"""
			Validates the current status of the parcel and change it if it's possible.

			# Parcel was waiting for receipt, now is mark as delivered. waiting for confirmation.
			# Parcel was waiting for receipt or confirmation and now is waiting for the departure.
			# Parcel was not received and not confirmed, but has appear on the warehouse receipt.

			# TODO: Validate this when status is changed on Form-View or List-View
				"""
		psm = ParcelStateMachine(status=self.status)
		psm.transition(new_status)

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
		shipment_settings = frappe.db.get_single_value("Shipment Settings", "barcode_type")
		# barcode_type = shipment_settings.barcode_type
		self.barcode = generate_barcode(shipment_settings)

	# @property
	# def explained_status(self):
	# 	""" This returns a detailed explanation of the current status of the Parcel and compatible colors. """
	# 	# TODO: Python 3.10: Migrate to switch case or Improve performance?
	# 	# frappe.local.lang = LocaleLanguage.SPANISH  # Little Hack

	# 	message, color = [], 'blue'  # TODO: Add more colors? Check frappe colors

	# 	match self.status:
	# 		case Status.AWAITING_RECEIPT:
	# 			message = [StatusMessage.TRANSPORTATION_NOT_DELIVERED_YET]

	# 			if self.carrier_est_delivery:  # The carrier has provided an estimated delivery date
	# 				est_delivery_diff = frappe.utils.date_diff(None, self.carrier_est_delivery)  # Diff from estimated to today
	# 				est_delivery_date = frappe.utils.format_date(self.carrier_est_delivery, 'medium')  # readable date

	# 				if est_delivery_diff == 0:  # Delivery is today
	# 					message.append(StatusMessage.ESTIMATED_DELIVERY_DATE_TODAY)
	# 				elif est_delivery_diff == -1:  # Delivery is tomorrow
	# 					message.append(StatusMessage.ESTIMATED_DELIVERY_DATE_TOMORROW)
	# 				elif est_delivery_diff < 0:  # Delivery is in the next days
	# 					# message.append('La fecha programada es: {}'.format(est_delivery_date))
	# 					message.append(StatusMessage.ESTIMATED_DELIVERY_DATE.value.replace('[DATE]', est_delivery_date))
	# 				else:  # Delivery is late
	# 					color = 'pink'
	# 					# message.append('Esta retrasado. Debio de ser entregado el: {}'.format(est_delivery_date))
	# 					message.append(StatusMessage.DELAYED_DELIVERY_DATE.value.replace('[DATE]', est_delivery_date))
	# 					message.append(StatusMessage.CONTACT_YOUR_PROVIDER_FOR_INFO)
	# 			else:
	# 				color = 'yellow'
	# 				message.append(StatusMessage.NOT_DELIVERY_DATE_ESTIMATED)

	# 		case Status.AWAITING_CONFIRMATION:
	# 			message, color = self._awaiting_confirmation_or_in_extraordinary_confirmation()
	# 		case Status.IN_EXTRAORDINARY_CONFIRMATION:
	# 			message, color = self._awaiting_confirmation_or_in_extraordinary_confirmation()
	# 		case Status.AWAITING_DEPARTURE:
	# 			# TODO: Add Warehouse Receipt date, # TODO: Add cargo shipment calendar
	# 			# cargo_shipment = frappe.get_cached_doc('Cargo Shipment', self.cargo_shipment)
    
	# 			# TODO: What if we dont have real delivery date. Or signature
	# 			if self.carrier_real_delivery:
	# 				message = [
	# 					StatusMessage.TRANSPORTER_DELIVERY_DATE.value.replace(
	# 						'[DATE]',
	# 						frappe.utils.format_datetime(self.carrier_real_delivery, 'medium')
	# 					),
	# 				]
	# 			if self.signed_by:
	# 				message.append(StatusMessage.SIGNED_BY.value.replace('[SIGNER]', str(self.signed_by)))
	# 				# 'Firmado por {}'.format(self.carrier_real_delivery, self.signed_by),
	# 				# 'Fecha esperada de recepcion en Managua: {}'.format(cargo_shipment.expected_arrival_date),

	# 			message.append('Embarque: {}'.format(self.cargo_shipment))

	# 		case Status.IN_TRANSIT:
	# 			# TODO: Add Departure date and est arrival date
	# 			if not self.cargo_shipment:
	# 				return {'message': [StatusMessage.NO_CARGO_SHIPPING], color: 'red'}

	# 			cargo_shipment = frappe.get_cached_doc('Cargo Shipment', self.cargo_shipment)

	# 			color = 'purple'

	# 			message = [
	# 				StatusMessage.PACKAGE_IN_TRANSIT_TO_DESTINATION,
	# 				StatusMessage.DEPARTURE_DATE.value.replace('[DATE]', str(cargo_shipment.departure_date)),
	# 				StatusMessage.ESTIMATED_RECEPTION_DATE.value.replace('[DATE]', str(cargo_shipment.expected_arrival_date)),
	# 				StatusMessage.CARGO_SHIPMENT.value.replace('[SHIPMENT]', self.cargo_shipment)
	# 			]
	# 		case Status.IN_CUSTOMS:
	# 			message, color = [StatusMessage.PACKAGE_IN_CUSTOMS], 'gray'
	# 		case Status.SORTING:
	# 			message, color = [StatusMessage.PACKAGE_IN_OFFICE_SORTING], 'blue'
	# 		case Status.TO_BILL:
	# 			message, color = [StatusMessage.PACKAGE_IN_OFFICE_SORTING], 'blue'

	# 		case Status.UNPAID:
	# 			message, color = [StatusMessage.PACKAGE_READY], 'blue'
	# 		case  Status.FOR_DELIVERY_OR_PICKUP:
	# 			message, color = [StatusMessage.PACKAGE_READY], 'blue'

	# 		case Status.FINISHED:
	# 			message, color = [StatusMessage.PACKAGE_FINISHED], 'green'  # TODO: Show invoice, delivery and payment details.
	# 		case Status.CANCELLED:
	# 			message, color = [StatusMessage.CONTACT_AGENT_FOR_PACKAGE_INFO], 'orange'
	# 		case Status.NEVER_ARRIVED:
	# 			message, color = [StatusMessage.PACKAGE_NEVER_ARRIVED], 'red'
	# 			message.append(StatusMessage.CONTACT_FOR_MORE_INFO)
	# 		case Status.RETURNED_TO_SENDER:
	# 			message, color = [StatusMessage.PACKAGE_RETURNED], 'red'
	# 			message.append(StatusMessage.CONTACT_FOR_MORE_INFO)

	# 		case _:
	# 			...

	# 	return {'message': message, 'color': color}


	# def validate(self):
	# 	self.validate_debit_to_acc()


	def on_submit(self):
		self.make_gl_entries()
		self.mark_parcel_as_never_arrived()
		self.mark_parcel_as_returned_to_sender()
		self.mark_parcel_as_finished_to_sender()


	def on_change(self):
		self.mark_parcel_as_never_arrived()
		self.mark_parcel_as_returned_to_sender()
		self.mark_parcel_as_finished_to_sender()

	@frappe.whitelist()
	def calculate_total_amount(doc):
		total_amount = sum(row.get("shipping_amount", 0) for row in doc.get("warehouse_receipt_lines", []))
		# frappe.msgprint(f"Total Amount: {total_amount}")
		return total_amount



	def make_gl_entries(self, gl_entries=None, cancel=0, from_repost=False):
		from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries
		if not gl_entries:
			gl_entries = self.get_gl_entries()

		if gl_entries:

			# if self.docstatus == 1:
			# 	make_gl_entries(
			# 		gl_entries,
			# 		merge_entries=False,
			# 		from_repost=from_repost,
			# 	)

			if cancel:
				cancel_exchange_gain_loss_journal(frappe._dict(doctype=self.doctype, name=self.name))
				make_reverse_gl_entries(gl_entries, partial_cancel=True)


			else :
				make_gl_entries(
					gl_entries,
					merge_entries=False,
					from_repost=from_repost,
				)
		
			# from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt

			# update_outstanding_amt(
			# 	self.debit_to,
			# 	"Customer",
			# 	self.customer,
			# 	self.doctype,
			# 	self.return_against if cint(self.is_return) and self.return_against else self.name,
			# )


 
	def get_gl_entries(self, warehouse_account=None):
		from erpnext.accounts.general_ledger import merge_similar_entries

		gl_entries = []

		self.make_agent_gl_entry(gl_entries)
		# self.make_parcel_gl_entries(gl_entries)
		self.make_agent_commission_gl_entry(gl_entries)


		return gl_entries
		
	def make_agent_gl_entry(self, gl_entries):
		settings = frappe.get_value('Shipment Settings', None, 'commission')

		# إذا كانت الإعدادات تشير إلى أن العمولة يجب أن تُحسب
		if settings != 'From Parcel':
			self.total_commission = 0
		gl_entries.append(
			self.get_gl_dict(
				{
					"account": self.debit_to,
					"party_type": "Customer",
					"party": self.shipper_name,
					"posting_date": self.order_date,
					"against": self.agent_account,
					"credit": self.total,

					# "debit_in_account_currency": self.total
					# if self.party_account_currency == self.company_currency
					# else grand_total,
					# "against_voucher": against_voucher,
					# "against_voucher_type": self.doctype,
					# "cost_center": self.cost_center,
					# "project": self.project,
				},
				# self.party_account_currency,
				item=self,
			)
		)
		gl_entries.append(
			self.get_gl_dict(
				{
					"account": self.receiving_account,
					"posting_date": self.order_date,

					"against": self.debit_to,
					"debit": self.total - self.total_commission,
					# "credit_in_account_currency": self.total,
					# "against_voucher": self.name,
					# "against_voucher_type": self.doctype,
					# "cost_center": self.cost_center,
					# "project": self.project,
				},
				item=self,
			)
		)


	def make_agent_commission_gl_entry(self, gl_entries):
		settings = frappe.get_value('Shipment Settings', None, 'commission')

		# إذا كانت الإعدادات تشير إلى أن العمولة يجب أن تُحسب
		if settings != 'From Warehouse':
			if self.agent_account and self.total_commission:
				gl_entries.append(
					self.get_gl_dict(
						{
							"account": self.agent_account,
							"posting_date": self.order_date,
							"party_type": "Agent",
                            "party": self.agent,

							"against": self.debit_to,
							"debit": self.total_commission,
							# "credit_in_account_currency": self.total,
							# "against_voucher": self.name,
							# "against_voucher_type": self.doctype,
							# "cost_center": self.cost_center,
							# "project": self.project,
						},
						item=self,
					)
				)

	def mark_parcel_as_never_arrived(self):
		if self.not_arrived and self.status != 'Never Arrived':
			self.db_set('status', 'Never Arrived', update_modified=False)

			#frappe.msgprint(_("The parcel {0} has been marked as 'Never Arrived'.").format(self.name))

	def mark_parcel_as_finished_to_sender(self):
		if self.is_parcel_received and self.status != 'Finished':
			self.db_set('status', 'Finished', update_modified=False)

			
	def mark_parcel_as_returned_to_sender(self):
		if self.returned_to_sender and self.status != 'Returned to Sender':
				self.db_set('status', 'Returned to Sender', update_modified=False)

			#frappe.msgprint(_("The parcel {0} has been marked as 'Never Arrived'.").format(self.name))



		# def make_parcel_gl_entries(self, gl_entries):
		# 	for item in self.get("warehouse_receipt_lines"):
		# 		if item.shipping_amount:
		# 			if self.commission_rate:
		# 				commission_amount = item.shipping_amount * (self.commission_rate / 100)
		# 				shipping_amount_after_commission = item.shipping_amount - commission_amount
		# 			else:
		# 				# إذا لم توجد نسبة العمولة، استخدم قيمة الشحن كما هي
		# 				shipping_amount_after_commission = item.shipping_amount

		# 			income_account = self.paid_to
		# 			account_currency = get_account_currency(income_account)
		# 			gl_entries.append(
		# 				self.get_gl_dict(
		# 					{
		# 						"account": income_account,
		# 						"against": self.agent,
		# 						"credit": flt(shipping_amount_after_commission, item.precision("shipping_amount")),
		# 						"credit_in_account_currency": flt(shipping_amount_after_commission, item.precision("shipping_amount")),
		# 						"parcel": item.parcel,
		# 					},
		# 					account_currency,
		# 					item=item,
		# 				)
		# 			)


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

	def validate_debit_to_acc(self):
			if not self.debit_to:
				self.debit_to = get_party_account("Customer", self.shipper_name, self.company)
				if not self.debit_to:
					self.raise_missing_debit_credit_account_error("Customer", self.shipper_name)

			account = frappe.get_cached_value(
				"Account", self.debit_to, ["account_type", "report_type", "account_currency"], as_dict=True
			)

			if not account:
				frappe.throw(_("Debit To is required"), title=_("Account Missing"))

@frappe.whitelist()
def get_account_for_customer(agent, company, docname=None):
    agent_doc = frappe.get_doc("Customer", agent)
    
    for row in agent_doc.accounts:
        if row.company == company:
            return row.account
    if agent_doc.customer_group:
        agent_group_doc = frappe.get_doc("Customer Group", agent_doc.customer_group)
        
        for row in agent_group_doc.accounts:
            if row.company == company:
                return row.account
    
    settings_doc = frappe.get_single("Shipment Settings")  
    if settings_doc:
        for row in settings_doc.accounts: 
            if row.company == company:
                return row.account
    
    frappe.msgprint(_("No account found for the selected company, agent, or agent group. Please choose one."))
    return None



@frappe.whitelist()
def get_create_invoice_setting():
    return frappe.db.get_single_value("Shipment Settings", "create_invoice")


@frappe.whitelist()
def create_sales_invoice(doc, rows):
    doc = frappe.get_doc(json.loads(doc))
    rows = json.loads(rows)
    
    if not rows:
        return

    auto_create_invoice = frappe.db.get_single_value("Shipment Settings", "create_invoice")
    auto_submit_invoice = frappe.db.get_single_value("Shipment Settings", "is_submit")

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

    if auto_create_invoice:
        # إنشاء الفاتورة تلقائيًا
        frappe.flags.ignore_account_permission = True
        invoice.set_taxes()
        invoice.set_missing_values()
        invoice.flags.ignore_mandatory = True
        invoice.calculate_taxes_and_totals()
        invoice.insert(ignore_permissions=True)
        
        if auto_submit_invoice:
            invoice.submit()

        for item in doc.content:
            if item.name in [i["name"] for i in rows]:
                item.invoice = invoice.name
        
        doc.save()
        frappe.msgprint(_("Sales Invoice {0} Created").format(invoice.name), alert=True)
        return invoice
    else:
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

@frappe.whitelist()
def get_item_price(item_code, price_list=None):
    filters = {'item_code': item_code}
    if price_list:
        filters['price_list'] = price_list
    
    item_price = frappe.get_all('Item Price', filters=filters, fields=['price_list_rate'], order_by='valid_from desc', limit=1)
    
    if item_price:
        return item_price[0].price_list_rate
    else:
        frappe.throw(f"Price not found for item {item_code}")
@frappe.whitelist()

# def calculate_shipping_amount(length, width, height):
#     try:
#         # تحويل النصوص إلى أعداد
#         length = float(length)
#         width = float(width)
#         height = float(height)
        
#         # حساب الحجم
#         volume = length * width * height
        
#         # قواعد التسعير بالحجم
#         if volume < 10:
#             return 100
#         elif 10 <= volume < 20:
#             return 200
#         elif 20 <= volume < 30:
#             return 300
#         else:
#             return 400
#     except ValueError as e:
#         return f"Error: {str(e)}"
    
	
@frappe.whitelist()
def calculate_shipping_amount_by_item_group( item_code=None, actual_weight=None, length=None ,width=None, height=None):
    item_group = frappe.db.get_value('Item', {'item_code': item_code}, 'item_group')

    price_rule = frappe.get_all('Parcel Price Rule',
        filters={'item_group': item_group},
        fields=['name']
    )

    if price_rule:
        conditions = frappe.get_all('Parcel Rule Condition',
            filters={
                'parent': price_rule[0].name,
                'from_value': ['<=', actual_weight],  # استخدم actual_weight مباشرة
                'to_value': ['>=', actual_weight]     # استخدم actual_weight مباشرة
            },
            fields=['shipping_amount']
        )

        if conditions:
            shipping_amount = conditions[0].shipping_amount
            frappe.log(f"Shipping Amount: {shipping_amount}")  # طباعة القيمة المرجعة
            return shipping_amount
    
    frappe.log("No suitable shipping condition found. Returning 0.")  # طباعة إذا لم يتم العثور على قاعدة مناسبة
    return 0
@frappe.whitelist()
def calculate_shipping_amount_by_rule(shipping_rule=0, item_code=None, actual_weight=None, length=None ,width=None, height=None):
    
    
    if shipping_rule == 'Volumetric Weight':
        
        if length is not None and width is not None and height is not None:
            try:
                length = float(length)
                width = float(width)
                height = float(height)
                
                volume = length * width * height
                
                if volume < 10:
                    return 100
                elif 10 <= volume < 20:
                    return 200
                elif 20 <= volume < 30:
                    return 300
                else:
                    return 400
            except ValueError as e:
                return f"Error: {str(e)}"
        else:
            return "Error: Length, width, and height are required for volumetric weight calculation."
    
    elif  shipping_rule == 'Item Group':
            item_group = frappe.db.get_value('Item', {'item_code': item_code}, 'item_group')

            price_rule = frappe.get_all('Parcel Price Rule',
                filters={'item_group': item_group},
                fields=['name']
            )

            if price_rule:
                conditions = frappe.get_all('Parcel Rule Condition',
                    filters={
                        'parent': price_rule[0].name,
                        'from_value': ['<=', actual_weight],
                        'to_value': ['>=', actual_weight]
                    },
                    fields=['shipping_amount']
                )

                if conditions:
                    shipping_amount = conditions[0].shipping_amount
                    frappe.log(f"Shipping Amount: {shipping_amount}")
                    return shipping_amount
            
            frappe.log("No suitable shipping condition found. Returning 0.")
            return 0
    elif  shipping_rule == 'Actual Weight':
          actual_weight = float(actual_weight)
          return actual_weight
    elif  shipping_rule == 'Fixed':
          fixed=frappe.get_value('Parcel Price Rule',shipping_rule,'shipping_amount')
          return fixed
    else:
            return "Error: Item code and actual weight are required for item group calculation."
    