from enum import StrEnum
from frappe import _

class Status(StrEnum):
    """ Warehouse Receipt Statuses """
    
    AWAITING_DEPARTURE = 'Awaiting Departure'
    IN_TRANSIT = 'In Transit'
    OPEN = 'Open'
    FINISHED = 'Finished'
    SORTING = 'Sorting'
   


    AWAITING_RECEIPT = 'Awaiting Receipt'
    AWAITING_CONFIRMATION = 'Awaiting Confirmation'
    IN_EXTRAORDINARY_CONFIRMATION = 'In Extraordinary Confirmation'
    IN_CUSTOMS = 'In Customs'
    TO_BILL = 'To Bill'
    UNPAID = 'Unpaid'
    FOR_DELIVERY_OR_PICKUP = 'For Delivery or Pickup'
    CANCELLED = 'Cancelled'
    NEVER_ARRIVED = 'Never Arrived'
    RETURNED_TO_SENDER = 'Returned to Sender'



class StatusMessage(StrEnum):
    # Warehouse Receipt Explanations
    PACKAGE_AWAITING_DEPARTURE = _('The package is awaiting departure.')
    PACKAGE_IN_TRANSIT = _('The package is in transit to its destination.')
    PACKAGE_OPEN = _('The package is open and awaiting further processing.')
    PACKAGE_FINISHED = _('The package processing is completed.')
    PACKAGE_SORTING = _('The package is being sorted in the warehouse.')

    CONTACT_AGENT_FOR_PACKAGE_INFO = _('Contact an agent for more information about the package.')
    PACKAGE_NEVER_ARRIVED = _('The package never arrived at the warehouse.')
    PACKAGE_RETURNED = _('The package was returned to the sender.')

    # Additional messages for various scenarios can be added here
    ESTIMATED_DEPARTURE_DATE = _('Estimated departure date: [DATE]')
    ACTUAL_DEPARTURE_DATE = _('Actual departure date: [DATE]')
    ESTIMATED_ARRIVAL_DATE = _('Estimated arrival date: [DATE]')
    ACTUAL_ARRIVAL_DATE = _('Actual arrival date: [DATE]')
