import frappe
import erpnext
from frappe import _
from cargo_management.utils import get_list_from_child_table
from frappe.model.document import Document
from .utils import WarehouseStateMachine
from .constant import Status, StatusMessage



from erpnext.accounts.general_ledger import (
	make_gl_entries,
	make_reverse_gl_entries,
	process_gl_map,
)
from erpnext.accounts.utils import (
	create_gain_loss_journal,
	get_account_currency,
	get_currency_precision,
	get_fiscal_years,
	validate_fiscal_year,
)
from frappe.utils import cint, comma_or, flt, getdate, nowdate
from erpnext.accounts.utils import (
	cancel_exchange_gain_loss_journal,
	get_account_currency,
	get_balance_on,
	get_outstanding_invoices,
	get_party_types_from_account_type,
)
from erpnext.accounts.party import get_party_account

from erpnext.accounts.doctype.bank_account.bank_account import (
	get_bank_account_details,
	get_default_company_bank_account,
	get_party_bank_account,
)
from erpnext.accounts.doctype.invoice_discounting.invoice_discounting import (
	get_party_account_based_on_invoice_discounting,
)
from erpnext.controllers.accounts_controller import AccountsController

class WarehouseReceipt(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from cargo_management.warehouse_management.doctype.warehouse_receipt_line.warehouse_receipt_line import WarehouseReceiptLine
		from frappe.types import DF

		agent: DF.Link
		agent_account: DF.Link
		amended_from: DF.Link | None
		carrier_est_gross_weight: DF.Float
		commission_rate: DF.Float
		company: DF.Link
		cost_center: DF.Link | None
		departure_date: DF.Date | None
		description: DF.SmallText | None
		mode_of_payment: DF.Link | None
		naming_series: DF.Literal["SHIP-WAR-.YYYY.-"]
		paid_from_account_balance: DF.Currency
		paid_from_account_currency: DF.Link | None
		paid_to: DF.Link
		paid_to_account_balance: DF.Currency
		paid_to_account_currency: DF.Link | None
		party_balance: DF.Currency
		posting_date: DF.Date
		received_amount: DF.Currency
		source_exchange_rate: DF.Float
		status: DF.Literal["Open", "Awaiting Departure", "In Transit", "Sorting", "Finished"]
		target_exchange_rate: DF.Float
		total_commission: DF.Currency
		total_shipment_amount: DF.Currency
		total_shipping_price: DF.Float
		transportation: DF.Literal["", "Sea", "Air"]
		volumetric_weight: DF.Float
		warehouse_est_gross_weight: DF.Float
		warehouse_receipt_lines: DF.Table[WarehouseReceiptLine]
	# end: auto-generated types
		# begin: auto-generated types
		# This code is auto-generated. Do not modify anything in this block.


	def on_update(self):
		""" Add Warehouse Receipt Link to the Package. This allows to have mutual reference WR to Package. """
		# FIXME: If Warehouse Receipt is deleted, remove link from Package
		# TODO: Add extra fields from Warehouse Receipt -> Receipt Date & Weight

		# We only change the warehouse_receipt field if it is different from current.
		packages = get_list_from_child_table(self.warehouse_receipt_lines, 'parcel')

		if not packages:
			return
		if self.name:
			frappe.db.sql("""
			UPDATE tabParcel
			SET warehouse_receipt = %(wr_name)s
			WHERE name IN %(packages)s AND COALESCE(warehouse_receipt, '') != %(wr_name)s
			""", {
				'wr_name': self.name,
				'packages': packages
			})

	# TODO: Actually change the status after the package is validated and creadted. maybe at status change from draft to open?

	# def change_status(self, new_status):
	# 	"""
	# 		Validates the current status of the parcel and change it if it's possible.

	# 		# Parcel was waiting for receipt, now is mark as delivered. waiting for confirmation.
	# 		# Parcel was waiting for receipt or confirmation and now is waiting for the departure.
	# 		# Parcel was not received and not confirmed, but has appear on the warehouse receipt.

	# 		# TODO: Validate this when status is changed on Form-View or List-View
	# 			"""
	# 	psm = ParcelStateMachine(status=self.status)
	# 	psm.transition(new_status)

	
	# 	if (self.status != new_status and \
	# 		(self.status == 'Awaiting Receipt' and new_status in ['Awaiting Confirmation', 'Returned to Sender']) or \
	# 		(self.status in ['Awaiting Receipt', 'Awaiting Confirmation', 'In Extraordinary Confirmation', 'Cancelled'] and new_status == 'Awaiting Departure') or \
	# 		(self.status == 'Awaiting Departure' and new_status == 'In Transit') or \
	# 		(self.status in ['Awaiting Receipt', 'Awaiting Confirmation', 'In Extraordinary Confirmation', 'Awaiting Departure', 'In Transit', 'Cancelled'] and new_status == 'Sorting') or \
	# 		(self.status not in ['Unpaid', 'For Delivery or Pickup', 'Finished'] and new_status == 'To Bill') or \
	# 		(self.status in ['Sorting', 'To Bill'] and new_status == 'Unpaid') or \
	# 		(self.status == 'Unpaid' and new_status == 'For Delivery or Pickup')):
	# 		self.status = new_status
	# 		return True

	# 	return False

	

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
	###########الاصل
	# def change_status(self, new_status):
	# 	"""
	# 	Validates the current status of the warehouse receipt and change it if it's possible.
	# 	"""
	# 	if self.status != new_status and \
	# 		(self.status == 'Open' and new_status == 'Awaiting Departure') or \
	# 		(self.status in ['Open', 'Awaiting Departure'] and new_status == 'In Transit') or \
	# 		(self.status in ['Open', 'Awaiting Departure', 'In Transit'] and new_status == 'Sorting') or \
	# 		(self.status in ['Open', 'Awaiting Departure', 'In Transit', 'Sorting'] and new_status == 'Finished'):
	# 		self.status = new_status
	# 		return True

	# 	return False
	def change_status(self, new_status):
		"""
			Validates the current status of the warehouse receipt and changes it if it's possible.
			
			# Warehouse Receipt was awaiting departure, now it's in transit or sorting.
			# Warehouse Receipt was open and now is finished or sorting.
			# Warehouse Receipt was not finished but has moved to sorting.
			# TODO: Validate this when status is changed on Form-View or List-View
		"""
		print(f"Attempting to change status to: {new_status}")

		wsm = WarehouseStateMachine(status=self.status)
		wsm.transition(new_status)

		if (self.status != new_status and \
			(self.status == 'Awaiting Departure' and new_status in ['In Transit', 'Sorting']) or \
			(self.status == 'Open' and new_status in ['Finished', 'Sorting']) or \
			(self.status == 'In Transit' and new_status == 'Sorting') or \
			(self.status == 'Sorting' and new_status == 'Finished')):
			self.status = new_status
			return True

		return False
	@property
	def explained_status(self):
		""" This returns a detailed explanation of the current status of the Warehouse Receipt and compatible colors. """
		message, color = [], 'blue'  # Default color

		match self.status:
			case Status.AWAITING_DEPARTURE:
				message.append('The warehouse receipt is waiting for departure.')
				color = 'yellow'

			case Status.IN_TRANSIT:
				message.append('The warehouse receipt is currently in transit.')
				color = 'purple'

			case Status.OPEN:
				message.append('The warehouse receipt is open and awaiting further actions.')
				color = 'blue'

			case Status.FINISHED:
				message.append('The warehouse receipt process is finished.')
				color = 'green'

			case Status.SORTING:
				message.append('The warehouse receipt is currently being sorted.')
				color = 'blue'

			case _:
				message.append('Status unknown.')
				color = 'gray'

		return {'message': message, 'color': color}




	# def before_save(self):
	# 	if self.docstatus == 1:

	# 	# if self.status != 'Awaiting Departure':
	# 		self.status = 'Awaiting Departure'
	# 	if not self.change_status('Awaiting Departure'):
	# 		frappe.msgprint(_(self.status ))
		
		# frappe.throw(_("Failed to update status to 'Awaiting Departure'."))
	# تأكيد أن المستند تم حفظه وتحقق من استلام الطرود

	def update_parcel_status1_to_awaiting_departure(self):
			parcels = get_list_from_child_table(self.warehouse_receipt_lines, 'parcel')
			
			# تغيير حالة كل طرد إلى "Awaiting Departure"
			for parcel in parcels:
				# تحميل الطرد المرتبط
				parcel_doc = frappe.get_doc('Parcel', parcel)
				if parcel_doc.status == 'Awaiting Receipt':  # تحقق من الحالة الحالية
					parcel_doc.change_status('Awaiting Confirmation')  # تحديث الحالة
					parcel_doc.save()  # حفظ التغييرات
					frappe.db.commit()  
	# تأكيد التغييرات في قاعدة البيانات

	# def before_save(self):
	# 	self.update_parcel_status_to_awaiting_departure()
	

	
	
	def on_submit(self):
		self.make_gl_entries()
		self.update_parcel_status_to_awaiting_departure()
		
		
		self.status = 'Awaiting Departure'
		self.save()

	def validate(self):
		self.update_parcel_status1_to_awaiting_departure()				

    # تحقق من أن المستند في حالة draft
		if self.docstatus == 0:
			if self.status != 'Awaiting Departure':
				if not self.is_new():  # تفحص إذا كان المستند جديدًا أو لا
					self.reload()
				
				self.status = 'Awaiting Departure'
				
				if not self.is_new():
					self.save()
					frappe.db.commit()

			

	def update_parcel_status_to_awaiting_departure(self):
				parcels = get_list_from_child_table(self.warehouse_receipt_lines, 'parcel')
				
				for parcel in parcels:
					parcel_doc = frappe.get_doc('Parcel', parcel)
					if parcel_doc.status == 'Awaiting Confirmation':  # تحقق من الحالة الحالية
						parcel_doc.change_status('Awaiting Departure')  # تحديث الحالة
						parcel_doc.save()  # 
						frappe.db.commit()  
	
	
	

	    
       
	# def before_save(self):
	# 	self.update_parcel_status1_to_awaiting_departure()

	# def before_cancel(self):
	# # فك الارتباط مع Payment Ledger Entry
	# 	payment_entries = frappe.get_all('Payment Ledger Entry', filters={'parcel': self.name})
	# 	for payment_entry in payment_entries:
	# 		frappe.db.set_value('Payment Ledger Entry', payment_entry.name, 'parcel', None)

		# gl_entries = frappe.get_all('GL Entry', filters={'voucher_no': self.name})
		# for gl_entry in gl_entries:
		# 	try:
		# 		# استدعاء دالة إلغاء قيد GL Entry
		# 		gl_doc = frappe.get_doc('GL Entry', gl_entry.name)
		# 		gl_doc.cancel()
		# 	except Exception as e:
		# 		frappe.throw(_("Could not cancel GL Entry {0}: {1}").format(gl_entry.name, str(e)))

		# frappe.msgprint(_("All related GL Entries have been cancelled successfully."))

	# def on_cancel(self):
	# هنا تقوم بالإلغاء النهائي للـ Parcel بعد فك الارتباط
		# frappe.db.set(self, 'status', 'Cancelled')
		# frappe.msgprint(_("Parcel has been cancelled successfully."))

		# self.make_gl_entries(cancel=1)


		

	
	
	# @frappe.whitelist()
	# def calculate_total_amount(doc):
	# 		total_amount = sum(row.get("shipping_amount", 0) for row in doc.get("warehouse_receipt_lines", [])) 
	# 		return total_amount




	def make_gl_entries(self, gl_entries=None, from_repost=False):
		from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries
		if not gl_entries:
			gl_entries = self.get_gl_entries()

		if gl_entries:

			if self.docstatus == 1:
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
		self.make_parcel_gl_entries(gl_entries)


		return gl_entries

	def make_agent_gl_entry(self, gl_entries):
		if self.commission_rate:
			shipping_amount_after_commission = self.total_shipment_amount - self.total_commission
		else:
			shipping_amount_after_commission = self.total_shipment_amount
		gl_entries.append(
			self.get_gl_dict(
				{
					"account": self.agent_account,
					"party_type": "Agent",
					"party": self.agent,
					"posting_date": self.posting_date,
					"against": self.paid_to,
					"debit": shipping_amount_after_commission,
					"debit_in_account_currency": shipping_amount_after_commission,
					"against_voucher": self.name,
					"against_voucher_type": self.doctype,
					"cost_center": self.cost_center,
					# "project": self.project,
				},
				item=self,
			)
		)
		if self.total_commission:
			gl_entries.append(
					self.get_gl_dict(
						{
							"account": self.paid_to,
							"posting_date": self.posting_date,
							"against": self.agent_account,
							"debit": self.total_commission,
							"debit_in_account_currency": self.total_commission,
							# "against_voucher": self.name,
							# "against_voucher_type": self.doctype,
							"cost_center": self.cost_center,
							# "project": self.project,
						},
						item=self,
					)
				)

	def make_parcel_gl_entries(self, gl_entries):
		for item in self.get("warehouse_receipt_lines"):
			if item.shipping_amount:
				income_account = self.paid_to
				account_currency = get_account_currency(income_account)
				gl_entries.append(
					self.get_gl_dict(
						{
							"account": income_account,
							"against": self.agent,
							"credit": flt(item.shipping_amount, item.precision("shipping_amount")),
							"credit_in_account_currency": flt(item.shipping_amount, item.precision("shipping_amount")),
							"parcel": item.parcel,
						},
						account_currency,
						item=item,
					)
				)

	# def make_parcel_gl_entries(self, gl_entries):
	# 	for item in self.get("warehouse_receipt_lines"):
	# 		if item.shipping_amount:
	# 			# income_account = item.income_account
	# 			income_account = self.paid_to
	
	# 			# amount, base_amount = self.get_amount_and_base_amount(item, 1)

	# 			account_currency = get_account_currency(income_account)
	# 			gl_entries.append(
	# 				self.get_gl_dict(
	# 					{
	# 						"account": income_account,
	# 						"against": self.agent,
	# 						"credit": flt(item.shipping_amount, item.precision("shipping_amount")),
	# 						"credit_in_account_currency": flt(item.shipping_amount, item.precision("shipping_amount")),
	# 						"parcel": item.parcel,
	# 						# "cost_center": item.cost_center,
	# 						# "project": item.project or self.project,
	# 						# "project": item.project or self.project,
	# 					},
	# 					account_currency,
	# 					item=item,
	# 				)
	# 			)

	# expense account gl entries
	# if cint(self.update_stock) and erpnext.is_perpetual_inventory_enabled(self.company):
	# 	gl_entries += super().get_gl_entries()




@frappe.whitelist()
def get_account_for_company(agent, company, docname=None):
    # Get the agent document
    agent_doc = frappe.get_doc("Agent", agent)
    
    # Check in the agent's accounts
    for row in agent_doc.accounts:
        if row.company == company:
            return row.account
    
    if agent_doc.agent_group:
        agent_group_doc = frappe.get_doc("Agent Group", agent_doc.agent_group)
        
        for row in agent_group_doc.accounts:
            if row.company == company:
                return row.account
    
    settings_doc = frappe.get_single("Shipment Settings")  # Replace "Settings" with your actual settings doctype name
    if settings_doc:
        for row in settings_doc.accounts:  # Replace 'default_accounts' with the appropriate field
            if row.company == company:
                return row.account
    
    frappe.msgprint(_("No account found for the selected company, agent, or agent group. Please choose one."))
    return None

@frappe.whitelist()
def get_rate_for_agent(agent):
    agent_doc = frappe.get_doc("Agent", agent)
    
    agent_rate = agent_doc.get("commission_rate")
    
    if not agent_rate:
        if agent_doc.agent_group:
            agent_group_doc = frappe.get_doc("Agent Group", agent_doc.agent_group)
            agent_rate = agent_group_doc.get("commission_rate")
    
    if not agent_rate:
        agent_rate = frappe.db.get_single_value('Shipment Settings', 'default_commission_rate')
    
    return agent_rate


@frappe.whitelist()
def get_account_for_mode_of_payment(agent, company):
    agent_doc = frappe.get_doc("Mode of Payment", agent)
    
    for row in agent_doc.accounts:
        if row.company == company:
            return row.default_account
    
    frappe.msgprint(_("No account found for the selected company and agent."))

@frappe.whitelist()
def calculate_commission(commission_rate, total):
		if total is None or commission_rate is None:
			return 0.0

		try:
			total = float(total)
			commission_rate = float(commission_rate)
		except ValueError:
			return 0.0
		commission = (total * commission_rate) / 100
		# frappe.msgprint(str(commission))

		return commission


@frappe.whitelist()
def calculate_rate(total, total_commission):
    if total is None or total_commission is None:
        return 0.0

    try:
        total = float(total)
        total_commission = float(total_commission)
    except ValueError:
        return 0.0

    if total == 0:
        return 0.0
    commission_rate = (total_commission / total) * 100
    return commission_rate
