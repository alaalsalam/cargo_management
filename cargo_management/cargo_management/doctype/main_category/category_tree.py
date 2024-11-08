import frappe

@frappe.whitelist()
def get_childre(doctype, parent=None, is_group=None):
    frappe.log(f"get_children called with: doctype={doctype}, parent={parent}, is_group={is_group}", "Debugging")

    if parent:
        children = frappe.db.sql("""
            SELECT 
                name as value, 
                is_group as expandable 
            FROM `tabSub Category` 
            WHERE parent_main_category=%s
        """, (parent), as_dict=1)
        
        # طباعة النتائج في الـ Log الخاص بـ Frappe
        frappe.log(children, "Children from Sub Category")
        return children
    else:
        main_categories = frappe.get_all('Main Category', filters={}, fields=['name as value', 'is_group as expandable'])
        
        # طباعة النتائج في الـ Log الخاص بـ Frappe
        frappe.log_error(main_categories, "Main Categories")
        return main_categories

@frappe.whitelist()
def add_node(parent, name, is_group, doctype="Main Category"):
    if parent:
        new_node = frappe.get_doc({
            'doctype': 'Sub Category',
            'parent_main_category': parent,
            'name': name,
            'is_group': is_group
        })
    else:
        # إذا لم يكن هناك parent، أضف تصنيفًا رئيسيًا
        new_node = frappe.get_doc({
            'doctype': 'Main Category',
            'category_name': name,
            'is_group': is_group
        })
    new_node.insert()
    return new_node.name
