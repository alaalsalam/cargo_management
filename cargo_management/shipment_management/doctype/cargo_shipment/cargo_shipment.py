import frappe
from cargo_management.utils import get_list_from_child_table
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, cint, flt, comma_or, now
import json
from frappe import _


class CargoShipment(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from cargo_management.shipment_management.doctype.cargo_shipment_line.cargo_shipment_line import CargoShipmentLine
        from cargo_management.shipment_management.doctype.cargo_shipment_warehouse.cargo_shipment_warehouse import CargoShipmentWarehouse
        from frappe.types import DF

        arrival_date: DF.Date | None
        cargo_shipment_lines: DF.Table[CargoShipmentLine]
        company: DF.Link | None
        currency: DF.Link
        departure_date: DF.Date
        estimated_gross_weight_by_carriers_in_pounds: DF.Float
        estimated_gross_weight_by_warehouse_in_pounds: DF.Float
        expected_arrival_date: DF.Date | None
        mute_emails: DF.Check
        naming_series: DF.Literal["SHIP-.YYYY.-"]
        net_total: DF.Currency
        pieces: DF.Int
        scan_barcode: DF.Data | None
        shipping_amount: DF.Currency
        status: DF.Literal["Awaiting Departure", "In Transit", "Sorting", "Finished"]
        supplier: DF.Link | None
        total: DF.Currency
        total_actual_weight: DF.Float
        total_qty: DF.Int
        transportation: DF.Literal["Sea", "Air"]
        warehouse_lines: DF.Table[CargoShipmentWarehouse]
    # end: auto-generated types

    def on_update(self):
        """ Add Departure Date to all Warehouse Receipt Linked """
        # TODO: What if cargo shipment is deleted?

        # TODO: Validate if any problem!
        frappe.db.sql("""
            UPDATE tabParcel
            SET cargo_shipment = %(cs_name)s
            WHERE `name` IN %(packages)s AND COALESCE(cargo_shipment, '') != %(cs_name)s
        """, {
            'cs_name': self.name,
            'packages': get_list_from_child_table(self.cargo_shipment_lines, 'package')
        })

        wrs_in_cs = get_list_from_child_table(self.cargo_shipment_lines, 'warehouse_receipt')
        if wrs_in_cs:  # If empty we don't touch the DB  # FIXME: Performance?
            frappe.db.sql("UPDATE `tabWarehouse Receipt` SET departure_date = %(date)s WHERE name IN %(wrs_in_cs)s", {
                'date': self.departure_date, 'wrs_in_cs': wrs_in_cs
            })

    def change_status(self, new_status):
        """ Validates the current status of the cargo shipment and change it if it's possible. """
        # TODO: Validate this when status is changed on Form-View or List-View

        # TODO: Finish
        if self.status != new_status and \
                (self.status == 'Awaiting Departure' and new_status == 'In Transit') or \
                (self.status in ['Awaiting Departure', 'In Transit'] and new_status == 'Sorting') or \
                (self.status == 'Sorting' and new_status =='Finished'):
            self.status = new_status
            return True

        return False



    @frappe.whitelist()
    def check_barcode(self, barcode):
        # Step 1: Filter the Cargo Registration based on the barcode
        cargo_registration = frappe.db.get_all('Parcel', filters={'barcode': barcode}, fields='*')
        
        if not cargo_registration:
            return {'success': False, 'error': 'Barcode not found.'}

        cargo_registration_name = cargo_registration[0]['name']  # الحصول على الاسم فقط
        
        # Step 2: Fetch the cargo details with the additional filter on manifest_number
        cargo_records = frappe.db.sql("""
            SELECT cr.* 
            FROM `tabParcel` cr
            JOIN `tabParcel Content` cd ON cr.name = cd.parent
            WHERE cr.name = %s AND cr.cargo_shipment IS NULL
        """, cargo_registration_name, as_dict=True)

        if not cargo_records:
            # Handle the case where no records are found
            return {'success': False, 'message': 'No cargo records found or cargo_shipment is not NULL.'}

        cargo_record = cargo_records[0]
        parcel = cargo_record.get('name')
        transportation = cargo_record.get('transportation')
        customer_name = cargo_record.get('shipper_name')
        description = cargo_record.get('description')

        # Step 3: Fetch the details from the Cargo Detail child table
        cargo_details = frappe.db.sql("""
            SELECT * FROM `tabParcel Content` WHERE parent = %s
        """, cargo_registration_name, as_dict=True)

        # Append details to cargo_shipment_lines
        self.append("cargo_shipment_lines", {
            "package": parcel,
            "transportation": transportation,
            "customer": customer_name,
            "description": description,
        })

        if self.save():
            cargo_doc = frappe.get_doc('Parcel', cargo_registration_name)
            if cargo_doc:
                cargo_doc.cargo_shipment = self.name
                cargo_doc.save()

            return {'success': True, 'message': 'Parcel added successfully.'}
        
        frappe.db.commit()

        return {'success': False, 'error': 'Failed to save the document.'}

    @frappe.whitelist()
    def update_manifest_numbers(self):
        # Step 1: Get all packages from Parcel table
        parcel_packages = frappe.get_all('Parcel', fields=['name'])

        # Step 2: Get all packages from manifest_cargo_details table
        manifest_cargo_details = frappe.get_all('Cargo Shipment Line', fields=['package'])

        # Step 3: Create a set of package names from manifest_cargo_details
        manifest_package_names = set([detail['package'] for detail in manifest_cargo_details])

        # Step 4: Loop through each package in Parcel and check if it's not in manifest_cargo_details
        for parcel in parcel_packages:
            if parcel['name'] not in manifest_package_names:
                # Step 5: Set cargo_shipment to None in Parcel doctype
                frappe.db.set_value('Parcel', parcel['name'], 'cargo_shipment', None)

        # Commit the changes to the database
        frappe.db.commit()

        return {"status": "success", "message": "Manifest numbers updated successfully."}


@frappe.whitelist()
def create_purchase_invoice(doc, rows):
    doc = frappe.get_doc(json.loads(doc))
    rows = json.loads(rows)
    
    if not rows:
        return

    items = []
    item_row_per = []

    for row in rows:
        item = frappe._dict({
            "item_code": row.get("item"),
            "qty": 1,
            "uom": frappe.get_value("Item", row["package"], "stock_uom"),
            "custom_parcel": row.get("package"),
            "rate": row["net_total"],
            "description": row.get("description"),
        })
        item_row_per.append([row, item])
        items.append(item)
    
    invoice = frappe.get_doc({
        "doctype": "Purchase Invoice",
        "supplier": doc.supplier,
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

    for item in doc.cargo_shipment_lines:
        if item.name in [i["name"] for i in rows]:
            item.invoice = invoice.name
    doc.save()

    frappe.msgprint(_("Sales Purchase {0} Created").format(invoice.name), alert=True)
    return invoice

