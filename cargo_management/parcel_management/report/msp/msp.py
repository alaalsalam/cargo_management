import frappe
def execute(filters=None):
    columns, data = [], []
    
    # تحديد الأعمدة
    columns = [
        {"label": "Parcel Name", "fieldname": "parcel_name", "fieldtype": "Link", "options": "Parcel", "width": 150},
        {"label": "Agent", "fieldname": "agent", "fieldtype": "Link", "options": "Agent", "width": 150},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Order Date", "fieldname": "order_date", "fieldtype": "Date", "width": 150},  # إضافة حقل Order Date
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150}  # إضافة حقل Company
    ]
    
    # جلب البيانات من جدول Parcel و Parcel Content
    query = """
        SELECT
            p.name AS parcel_name,
            p.agent,
            p.order_date,  -- جلب Order Date
            p.company,     -- جلب Company
            pc.item_code
        FROM
            `tabParcel` p
        LEFT JOIN
            `tabParcel Content` pc ON pc.parent = p.name
        WHERE
            p.agent IS NOT NULL
    """
    
    data = frappe.db.sql(query, as_dict=True)
    
    return columns, data
