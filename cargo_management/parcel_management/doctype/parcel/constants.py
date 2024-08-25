from enum import StrEnum
from frappe import _

class Status(StrEnum):
	""" Parcel Statuses """

	AWAITING_RECEIPT = 'Awaiting Receipt'
	AWAITING_CONFIRMATION = 'Awaiting Confirmation'
	IN_EXTRAORDINARY_CONFIRMATION = 'In Extraordinary Confirmation'  # FIXME: We can remove "IN"
	AWAITING_DEPARTURE = 'Awaiting Departure'
	IN_TRANSIT = 'In Transit'
	IN_CUSTOMS = 'In Customs'
	SORTING = 'Sorting'
	TO_BILL = 'To Bill'
	UNPAID = 'Unpaid'
	FOR_DELIVERY_OR_PICKUP = 'For Delivery or Pickup'  # FIXME, we can make to DELIVERY_OR_PICKUP
	FINISHED = 'Finished'
	CANCELLED = 'Cancelled'
	NEVER_ARRIVED = 'Never Arrived'
	RETURNED_TO_SENDER = 'Returned to Sender'


class StatusMessage(StrEnum):
	# Awaiting Receipt Explanations
	TRANSPORTATION_NOT_DELIVERED_YET = _('لم يقم الناقل بتسليم الطرد بعد.')
	ESTIMATED_DELIVERY_DATE_TODAY = _('تاريخ التسليم المقدر هو اليوم.')
	ESTIMATED_DELIVERY_DATE_TOMORROW = _('تاريخ التسليم المقدر هو غدًا.')
	ESTIMATED_DELIVERY_DATE = _('تاريخ التسليم المقدر هو: [DATE]')
	DELAYED_DELIVERY_DATE = _('تم تأخير التسليم. كان من المفترض أن يتم التسليم في: [DATE]')
	NOT_DELIVERY_DATE_ESTIMATED = _('لم يتم توفير تاريخ تسليم مقدر.')
	TRANSPORTATION_DELIVERED_DATE = _('يشير الناقل إلى التسليم في: [DATE]')
	SIGNED_BY = _('تم التوقيع بواسطة: [DATE]')
	HAS_BEEN_1_DAY = _('مر يوم واحد')
	HAS_BEEN_X_DAYS = _('مرت [DATE] أيام')
	WAIT_FOR_24_HOURS_CONFIRMATION = _('يرجى الانتظار 24 ساعة عمل لتأكيد استلام المستودع.')
	TRANSPORTER_INDICATE_ESTIMATE_DELIVERY_DATE = _('أشار الناقل إلى تاريخ تسليم تقريبي: [DATE]')
	PACKAGE_IN_EXTRAORDINARY_REVISION = _('الطرد قيد المراجعة الاستثنائية.')
	TRANSPORTER_DELIVERY_DATE = _('يشير الناقل إلى أن الطرد تم تسليمه في: [DATE]')
	NO_CARGO_SHIPPING = _('لا يوجد شحن بضائع')
	PACKAGE_IN_TRANSIT_TO_DESTINATION = _('الطرد قيد الترحيل إلى وجهته.')
	DEPARTURE_DATE = _('تاريخ الإرسال: [DATE]')
	ESTIMATED_RECEPTION_DATE = _('تاريخ الاستلام المتوقع في مناجوا: [DATE]')
	CARGO_SHIPMENT = _('شحنة: [DATE]')
	PACKAGE_IN_CUSTOMS = _('الطرد في عملية التخليص الجمركي.')
	PACKAGE_IN_OFFICE_SORTING = _('يتم فرز الطرد في المكتب.')
	PACKAGE_READY = _('الطرد جاهز للاستلام.')
	PACKAGE_FINISHED = _('تم إكمال الطرد.')
	CONTACT_AGENT_FOR_PACKAGE_INFO = _('اتصل بوكيل للحصول على مزيد من المعلومات حول الطرد.')
	PACKAGE_NEVER_ARRIVED = _('لم يصل الطرد إلى المستودع أبدًا.')
	PACKAGE_RETURNED = _('أعاد الناقل الطرد إلى البائع.')
	CONTACT_FOR_MORE_INFO = _('اتصل ببائعك و/أو الناقل لمزيد من المعلومات.')

	CONTACT_YOUR_PROVIDER_FOR_INFO = _('اتصل بالمزود الخاص بك للحصول على مزيد من المعلومات.')
# class StatusMessage(StrEnum):
#     # Awaiting Receipt Explanations
#     TRANSPORTATION_NOT_DELIVERED_YET = _('The carrier has not delivered the package yet.')
#     ESTIMATED_DELIVERY_DATE_TODAY = _('The scheduled delivery date is today.')
#     ESTIMATED_DELIVERY_DATE_TOMORROW = _('The scheduled delivery date is tomorrow.')
#     ESTIMATED_DELIVERY_DATE = _('The scheduled delivery date is: [DATE]')
#     DELAYED_DELIVERY_DATE = _('It is delayed. It should have been delivered on: [DATE]')
#     NOT_DELIVERY_DATE_ESTIMATED = _('No estimated delivery date has been provided.')

#     TRANSPORTATION_DELIVERED_DATE = _('The carrier indicates delivery on: [DATE]')
#     SIGNED_BY = _('Signed by: [DATE]')
#     HAS_BEEN_1_DAY = _('It has been 1 day')
#     HAS_BEEN_X_DAYS = _('It has been [DATE] days')
#     WAIT_FOR_24_HOURS_CONFIRMATION = _('Please wait 24 business hours for the warehouse to confirm receipt.')
#     TRANSPORTER_INDICATE_ESTIMATE_DELIVERY_DATE = _('The carrier indicated an approximate delivery date: [DATE]')
#     PACKAGE_IN_EXTRAORDINARY_REVISION = _('The package is undergoing extraordinary verification.')
#     TRANSPORTER_DELIVERY_DATE = _('The carrier indicates that the package was delivered on: [DATE]')
#     NO_CARGO_SHIPPING = _('There is no cargo shipment')
#     PACKAGE_IN_TRANSIT_TO_DESTINATION = _('The package is in transit to its destination.')
#     DEPARTURE_DATE = _('Dispatch date: [DATE]')
#     ESTIMATED_RECEPTION_DATE = _('Expected reception date in Managua: [DATE]')
#     CARGO_SHIPMENT = _('Shipment: [DATE]')
#     PACKAGE_IN_CUSTOMS = _('The package is in the customs clearance process.')
#     PACKAGE_IN_OFFICE_SORTING = _('The package is being sorted at the office.')
#     PACKAGE_READY = _('The package is ready for pickup.')
#     PACKAGE_FINISHED = _('Package Completed.')
#     CONTACT_AGENT_FOR_PACKAGE_INFO = _('Contact an agent for more information about the package.')
#     PACKAGE_NEVER_ARRIVED = _('The package never arrived at the warehouse.')
#     PACKAGE_RETURNED = _('The package was returned by the carrier to the seller.')
#     CONTACT_FOR_MORE_INFO = _('Contact your seller and/or carrier for more information.')

#     CONTACT_YOUR_PROVIDER_FOR_INFO = _('Contact your provider for more information.')
    
    
    
