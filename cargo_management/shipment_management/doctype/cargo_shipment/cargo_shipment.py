import frappe
from frappe.utils import today
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

        actual_arrival_date: DF.Date | None
        arrival_date: DF.Date | None
        cargo_shipment_lines: DF.Table[CargoShipmentLine]
        cargo_shipment_no: DF.Int
        company: DF.Link | None
        currency: DF.Link
        customs_amount: DF.Currency
        customs_arrival_date: DF.Date | None
        customs_supplier: DF.Link
        departure_date: DF.Date
        estimated_arrival_date: DF.Date
        estimated_gross_weight_by_carriers_in_pounds: DF.Float
        estimated_gross_weight_by_warehouse_in_pounds: DF.Float
        expected_arrival_date: DF.Date | None
        is_finished: DF.Check
        mute_emails: DF.Check
        naming_series: DF.Literal["SHIP-.YYYY.-"]
        net_total: DF.Currency
        pieces: DF.Int
        reservation_number: DF.Int
        scan_barcode: DF.Data | None
        shipping_amount: DF.Currency
        status: DF.Literal["Awaiting Departure", "Waiting for Arrival", "In Transit", "Sorting", "Finished"]
        supplier: DF.Link
        total: DF.Currency
        total_actual_weight: DF.Float
        total_qty: DF.Int
        transit_supplier: DF.Link
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

    # def update_parcel_status_to_waiting_for_arrival(self):

    #     parcels = get_list_from_child_table(self.cargo_shipment_lines, 'package')

    #     for parcel in parcels:

    #         parcel_doc = frappe.get_doc('Parcel', parcel)
            
    #         if parcel_doc.status == 'Awaiting Departure':  

    #             parcel_doc.change_status('In Transit')
    #             parcel_doc.save()  
    #             frappe.db.commit()      

    # def before_save(self):

    #     self.update_parcel_status_to_waiting_for_arrival()
    # def on_submit(self):

    #     self.update_parcel_status_to_waiting_for_arrival()

    # def update_parcel_status(self, status):
    #     # استرجاع قائمة الطرود من جدول cargo_shipment_lines
    #     parcels = get_list_from_child_table(self.cargo_shipment_lines, 'package')

    #     # تغيير حالة كل طرد بناءً على الحالة المدخلة
    #     for parcel in parcels:
    #         # تحميل الطرد المرتبط
    #         parcel_doc = frappe.get_doc('Parcel', parcel)
            
    #         # تحقق من الحالة الحالية للطرد قبل التحديث
    #         if parcel_doc.status == 'Awaiting Departure':  
    #             # تحديث حالة الطرد
    #             parcel_doc.status = status  # تعيين الحالة مباشرة
    #             parcel_doc.save()  # حفظ التغييرات

    #     # تأكيد التغييرات في قاعدة البيانات
    #     frappe.db.commit()

    # def before_save(self):
    #     # إذا كانت بيانات الجمارك مضافة، يتم تحديث الحالة إلى "In Customs"
    #     if self.customs_supplier:  # تحقق مما إذا كانت بيانات الجمارك موجودة
    #         frappe.msgprint(f"Customs Supplier found, updating status to In Customs")  # للتصحيح
    #         self.update_parcel_status('In Customs')
    #     else:
    #         frappe.msgprint(f"No Customs Supplier, updating status to In Transit")  # للتصحيح
    #         self.update_parcel_status('For Delivery or Pickup')

    # def on_submit(self):
    #     # نفس المنطق يمكن تطبيقه عند تقديم المستند
    #     if self.customs_supplier:  # تحقق مما إذا كانت بيانات الجمارك موجودة
    #         self.update_parcel_status('In Customs')
    #     else:
    #         self.update_parcel_status('For Delivery or Pickup')


    # def update_parcel_status(self, status):
    #     # استرجاع قائمة الطرود من جدول cargo_shipment_lines
    #     parcels = get_list_from_child_table(self.cargo_shipment_lines, 'package')

    #     # تغيير حالة كل طرد بناءً على الحالة المدخلة
    #     for parcel in parcels:
    #         # تحميل الطرد المرتبط
    #         parcel_doc = frappe.get_doc('Parcel', parcel)
            
    #         # تحقق من الحالة الحالية للطرد قبل التحديث
    #         if parcel_doc.status == 'Awaiting Departure':  
    #             # تحديث حالة الطرد
    #             parcel_doc.status = status  # تعيين الحالة مباشرة
    #             parcel_doc.save()  # حفظ التغييرات

    #     # تأكيد التغييرات في قاعدة البيانات
    #     frappe.db.commit()

    # def after_save(self):
    #     # تحقق من بيانات الجمارك أو النقل
  
    #     if not self.is_new():
    #         self.reload()
    #         self.save()
    #         frappe.db.commit()  
    #         if self.customs_supplier:  # إذا كانت بيانات الجمارك مضافة
    #             frappe.log(f"Customs Supplier found, updating status to In Customs")  # للتصحيح
    #             self.update_parcel_status('In Customs')
    #         elif self.transit_supplier:  # إذا كانت بيانات النقل مضافة
    #             frappe.db.commit()
    #             frappe.msgprint(f"Transit Supplier found, updating status to In Transit")  # للتصحيح
    #             self.update_parcel_status('In Transit')
    #             frappe.db.commit()
    #         else:  # إذا لم تكن هناك بيانات مضافة
    #             frappe.msgprint(f"No Customs or Transit Supplier found, updating status to For Delivery or Pickup")  # للتصحيح
    #             self.update_parcel_status('For Delivery or Pickup')
    #     elif self.is_new():
    #             if self.customs_supplier:  # إذا كانت بيانات الجمارك مضافة
    #                 frappe.log(f"Customs Supplier found, updating status to In Customs")  # للتصحيح
    #                 self.update_parcel_status('In Customs')
    #             elif self.transit_supplier:  # إذا كانت بيانات النقل مضافة
    #                 frappe.db.commit()
    #                 frappe.msgprint(f"Transit Supplier found, updating status to In Transit")  # للتصحيح
    #                 self.update_parcel_status('In Transit')
    #                 frappe.db.commit()
    #             else:  # إذا لم تكن هناك بيانات مضافة
    #                 frappe.msgprint(f"No Customs or Transit Supplier found, updating status to For Delivery or Pickup")  # للتصحيح
    #                 self.update_parcel_status('For Delivery or Pickup')

    def update_parcel_status(self, status):
        # استرجاع قائمة الطرود من جدول cargo_shipment_lines
        parcels = get_list_from_child_table(self.cargo_shipment_lines, 'package')

        for parcel in parcels:
            # تحميل الطرد المرتبط
            parcel_doc = frappe.get_doc('Parcel', parcel)
            
          
            parcel_doc.status = status
            parcel_doc.save()  # حفظ التغييرات

    # def before_save(self):
    #     # تحقق من بيانات الجمارك أو النقل
    #     if not self.is_new():
    #         # تحديث حالة الطرود فقط بدون إعادة الحفظ
    #         if self.customs_supplier:  # إذا كانت بيانات الجمارك مضافة
    #             frappe.msgprint(f"Customs Supplier found, updating status to In Customs")  # رسالة للمستخدم
    #             self.update_parcel_status('In Customs')
    #         elif self.transit_supplier:  # إذا كانت بيانات النقل مضافة
    #             frappe.msgprint(f"Transit Supplier found, updating status to In Transit")  # رسالة للمستخدم
    #             self.update_parcel_status('In Transit')
    #         else:  # إذا لم تكن هناك بيانات مضافة
    #             frappe.msgprint(f"No Customs or Transit Supplier found, updating status to For Delivery or Pickup")  # رسالة للمستخدم
    #             self.update_parcel_status('For Delivery or Pickup')

    #     # التعامل مع المستند الجديد
    #     elif self.is_new():
    #         if self.customs_supplier:  # إذا كانت بيانات الجمارك مضافة
    #             frappe.msgprint(f"Customs Supplier found, updating status to In Customs")  # رسالة للمستخدم
    #             self.update_parcel_status('In Customs')
    #         elif self.transit_supplier:  # إذا كانت بيانات النقل مضافة
    #             frappe.msgprint(f"Transit Supplier found, updating status to In Transit")  # رسالة للمستخدم
    #             self.update_parcel_status('In Transit')
    #         else:  # إذا لم تكن هناك بيانات مضافة
    #             frappe.msgprint(f"No Customs or Transit Supplier found, updating status to For Delivery or Pickup")  # رسالة للمستخدم
    #             self.update_parcel_status('For Delivery or Pickup')


    def on_submit(self):
        # نفس المنطق يمكن تطبيقه عند تقديم المستند
        if not self.is_new():
            self.save()
            frappe.db.commit()
        if self.customs_supplier:  # إذا كانت بيانات الجمارك مضافة
            self.update_parcel_status('In Customs')
        elif self.transit_supplier:  # إذا كانت بيانات النقل مضافة
            self.update_parcel_status('In Transit')
        else:  # إذا لم تكن هناك بيانات مضافة
            self.update_parcel_status('Waiting for Arrival')
        self.status = 'Awaiting Departure'
        self.save() 


    

    # def update_cargo_shipment_status():
    #     # جلب جميع مستندات Cargo Shipment التي لم تصل بعد وتطابق تاريخ اليوم مع departure_date
    #     shipments = frappe.get_all('Cargo Shipment', filters={'departure_date': today(), 'status': ['!=', 'Waiting for Arrival']})
        
    #     for shipment in shipments:
    #         # تحميل المستند
    #         shipment_doc = frappe.get_doc('Cargo Shipment', shipment.name)
            
    #         # تحديث الحالة إلى Waiting for Arrival
    #         shipment_doc.status = 'Waiting for Arrival'
    #         shipment_doc.save()
            
    #     frappe.db.commit()




    def update_warehouse_receipt_status(self, status):
        # استرجاع قائمة الويرهاوس ريسيبت من جدول cargo_shipment_lines
        warehouse_receipts = get_list_from_child_table(self.cargo_shipment_lines, 'warehouse_receipt')

        # تغيير حالة كل مستند Warehouse Receipt بناءً على الحالة المدخلة
        for receipt in warehouse_receipts:
            if receipt:  # تحقق من أن الحقل ليس فارغًا
                try:
                    # تحميل مستند Warehouse Receipt المرتبط
                    warehouse_receipt_doc = frappe.get_doc('Warehouse Receipt', receipt)
                    
                    # تحديث حالة المستند
                    warehouse_receipt_doc.status = status  # تعيين الحالة مباشرة
                    warehouse_receipt_doc.save()  # حفظ التغييرات

                except frappe.DoesNotExistError:
                    frappe.msgprint(f"Warehouse Receipt {receipt} does not exist", alert=True)

        # تأكيد التغييرات في قاعدة البيانات
        frappe.db.commit()

    # def before_save(self):
    #     # تحقق من وجود transit_supplier لتحديث حالة الويرهاوس ريسيبت
    #     if self.transit_supplier:  # إذا كانت بيانات النقل مضافة
    #         frappe.msgprint(f"Transit Supplier found, updating Warehouse Receipt status to In Transit")  # رسالة للمستخدم
    #         self.update_warehouse_receipt_status('In Transit')
    #     else:  # إذا لم تكن بيانات النقل مضافة
    #         frappe.msgprint(f"No Transit Supplier found, updating Warehouse Receipt status to Awaiting Departure")  # رسالة للمستخدم
    #         self.update_warehouse_receipt_status('Awaiting Departure')


    def validate(self):        
        # self.status = 'Awaiting Departure'
        self.mark_parcel_as_finished()
        if not self.is_new():
        # تحديث حالة الطرود فقط بدون إعادة الحفظ
            if self.customs_supplier:  # إذا كانت بيانات الجمارك مضافة
                frappe.msgprint(f"Customs Supplier found, updating status to In Customs")  # رسالة للمستخدم
                self.update_parcel_status('In Customs')
            elif self.transit_supplier:  # إذا كانت بيانات النقل مضافة
                frappe.msgprint(f"Transit Supplier found, updating status to In Transit")  # رسالة للمستخدم
                self.update_parcel_status('In Transit')
                self.update_warehouse_receipt_status('In Transit')
            else:  # إذا لم تكن هناك بيانات مضافة
                frappe.msgprint(f"No Customs or Transit Supplier found, updating status to For Delivery or Pickup")  # رسالة للمستخدم
                self.update_parcel_status('Waiting for Arrival')




        elif self.is_new():
            if self.customs_supplier:  # إذا كانت بيانات الجمارك مضافة
                frappe.msgprint(f"Customs Supplier found, updating status to In Customs")  # رسالة للمستخدم
                self.update_parcel_status('In Customs')
            elif self.transit_supplier:
                frappe.msgprint(f"Transit Supplier found, updating status to In Transit")  # رسالة للمستخدم
                self.update_parcel_status('In Transit')
                self.update_warehouse_receipt_status('In Transit')
            else:  # إذا لم تكن هناك بيانات مضافة
                frappe.msgprint(f"No Customs or Transit Supplier found, updating status to For Delivery or Pickup")  # رسالة للمستخدم
                self.update_parcel_status('Waiting for Arrival')

        if self.transit_supplier:  # إذا كانت بيانات النقل مضافة
            frappe.msgprint(f"Transit Supplier found, updating Warehouse Receipt status to In Transit")  # رسالة للمستخدم
            self.update_warehouse_receipt_status('In Transit')
        else:  # إذا لم تكن بيانات النقل مضافة
            frappe.msgprint(f"No Transit Supplier found, updating Warehouse Receipt status to Awaiting Departure")  # رسالة للمستخدم
            self.update_warehouse_receipt_status('Awaiting Departure')



        # if self.transit_supplier:  # إذا كانت بيانات النقل مضافة
        #     frappe.msgprint(f"Transit Supplier found, updating status to In Transit")  # للتصحيح
        #     self.update_parcel_status('In Transit')
        # else:  # إذا لم تكن هناك بيانات مضافة
        #     frappe.msgprint(f"No Customs or Transit Supplier found, updating status to For Delivery or Pickup")  # للتصحيح
        #     self.update_parcel_status('Awaiting Departure')


    def mark_parcel_as_finished(self):
            if self.is_finished and self.status != 'Finished':
                    self.db_set('status', 'Finished', update_modified=False)
                    
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
    
    auto_create_invoice = frappe.db.get_single_value("Shipment Settings", "create_invoice")
    auto_submit_invoice = frappe.db.get_single_value("Shipment Settings", "is_submit")

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

    if auto_create_invoice:

        frappe.flags.ignore_account_permission = True
        invoice.set_taxes()
        invoice.set_missing_values()
        invoice.flags.ignore_mandatory = True
        invoice.calculate_taxes_and_totals()
        invoice.insert(ignore_permissions=True)


        if auto_submit_invoice:
                    invoice.submit()

        for item in doc.cargo_shipment_lines:
            if item.name in [i["name"] for i in rows]:
                item.invoice = invoice.name
                
        doc.save()
        frappe.msgprint(_("Sales Purchase {0} Created").format(invoice.name), alert=True)
        return invoice
        # for item in doc.cargo_shipment_lines:
        #     if item.name in [i["name"] for i in rows]:
        #         item.invoice = invoice.name
        # doc.save()

        # frappe.msgprint(_("Sales Purchase {0} Created").format(invoice.name), alert=True)
        # return invoice
    else:
        return invoice



# @frappe.whitelist()
# def get_parcels_from_warehouses(warehouse_references):
#     parcels = []
#     # جلب جميع الطرود المرتبطة بالمخازن المحددة
#     if warehouse_references:
#         warehouse_receipts = frappe.get_all('Warehouse Receipt Line', 
#                                             filters={'parent': ['in', warehouse_references]},
#                                             fields=['parcel'])
        
#         for receipt in warehouse_receipts:
#             parcels.append(receipt.parcel)
    
#     return parcels


