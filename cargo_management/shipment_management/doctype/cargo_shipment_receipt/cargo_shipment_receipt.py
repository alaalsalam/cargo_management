import frappe
from frappe.model.document import Document
from cargo_management.utils import get_list_from_child_table

class CargoShipmentReceipt(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from cargo_management.shipment_management.doctype.cargo_shipment_receipt_line.cargo_shipment_receipt_line import CargoShipmentReceiptLine
		from frappe.types import DF

		amended_from: DF.Link | None
		arrival_date: DF.Date | None
		cargo_shipment: DF.Link
		cargo_shipment_receipt_lines: DF.Table[CargoShipmentReceiptLine]
		delivery_for_customer: DF.Check
		departure_date: DF.Date | None
		gross_weight: DF.Float
		mute_emails: DF.Check
		status: DF.Literal["Awaiting Receipt", "Sorting", "Finished"]
	# end: auto-generated types

	# TODO: Set customer on update!

	def validate(self):
		# TODO: make this sort function refresh the table
		sorted_list = sorted(
			self.cargo_shipment_receipt_lines,
			key=lambda item: (
				item.customer_name if item.customer_name else '',
				-float(item.gross_weight) if item.gross_weight else 0.00
			)
		)
		for i, item in enumerate(sorted_list, start=1):
			item.idx = i

	def change_status(self, new_status):
		""" Validates the current status of the cargo shipment receipt and change it if it's possible. """
		# TODO: Validate this when status is changed on Form-View or List-View

		# TODO: Finish
		if self.status != new_status and \
				(self.status == 'Awaiting Receipt' and new_status == 'Sorting') or \
				(self.status == 'Sorting' and new_status =='Finished'):
			self.status = new_status
			return True

		return False
	
	

	def update_parcel_status(self, status):
		# استرجاع قائمة الطرود من جدول cargo_shipment_lines
		parcels = get_list_from_child_table(self.cargo_shipment_receipt_lines, 'package')

		# تغيير حالة كل طرد بناءً على الحالة المدخلة
		for parcel in parcels:
			# تحميل الطرد المرتبط
			parcel_doc = frappe.get_doc('Parcel', parcel)
			parcel_doc.status = status  # تعيين الحالة مباشرة
			parcel_doc.save()
			# تحقق من الحالة الحالية للطرد قبل التحديث
			 
				# تحديث حالة الطرد
				  # حفظ التغييرات

		# تأكيد التغييرات في قاعدة البيانات
		frappe.db.commit()
		
	# def In_transit(self):
	# 		frappe.msgprint(f"تم تحديث حالة  إلى 'In Transit'")

	# 		# تحديث حالة cargo_shipment إلى In Transit عند الحفظ
	# 		if self.cargo_shipment:
	# 			cargo_shipment = frappe.get_doc('Cargo Shipment', self.cargo_shipment)
	# 			cargo_shipment.status = "In Transit"
	# 			cargo_shipment.save()
	# 			frappe.msgprint(f"تم تحديث حالة {cargo_shipment.name} إلى 'In Transit'")

			
	def In_transit(self):
		if self.cargo_shipment:
			cargo_shipment = frappe.get_doc('Cargo Shipment', self.cargo_shipment)

			# جلب جميع الطرود المرتبطة بـ Cargo Shipment
			all_parcels = frappe.get_all('Cargo Shipment Line', filters={'parent': cargo_shipment.name}, fields=['package'])

			# جلب جميع الطرود المستلمة في Cargo Shipment Receipt
			received_parcels = frappe.get_all('Cargo Shipment Receipt Line', filters={'parent': self.name}, fields=['package'])

			# استخراج قيم الحقول package من كل طرد
			all_parcel_packages = {parcel['package'] for parcel in all_parcels}
			received_parcel_packages = {parcel['package'] for parcel in received_parcels}

			# التحقق من مطابقة الطرود
			if all_parcel_packages == received_parcel_packages:
				cargo_shipment.status = "Completely Finished"
				frappe.msgprint(f"تم تحديث حالة {cargo_shipment.name} إلى 'منتهية بالكامل'")
			else:
				cargo_shipment.status = "Partially Finished"
				frappe.msgprint(f"تم تحديث حالة {cargo_shipment.name} إلى 'منتهية جزئيا'")
			cargo_shipment.save()


	def before_save(self):
		# تحقق من بيانات الجمارك أو النقل

		# if self.delivery_for_customer:
		# 	frappe.msgprint(f"Delivery for Customer is checked, updating status to For Delivery or Pickup")  # للتصحيح
			self.update_parcel_status('Finished')
		# else:  # إذا لم تكن هناك بيانات مضافة
		# 	frappe.msgprint(f"No For Delivery or Pickup")  # للتصحيح
		

	def on_submit(self):
		self.In_transit()
		# نفس المنطق يمكن تطبيقه عند تقديم المستند

		if self.delivery_for_customer:  # إذا كانت بيانات التسليم للعميل مفعلة
			self.update_parcel_status('Sorting')
		else:  # إذا لم تكن هناك بيانات مضافة
			frappe.msgprint(f"No For Delivery or Pickup")  # للتصحيح
