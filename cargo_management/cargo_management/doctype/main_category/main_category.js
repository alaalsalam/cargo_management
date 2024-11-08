frappe.treeview_settings["Main Category"] = {
    // عنوان شريط التنقل
    breadcrumb: "Main Category",
    
    // عدم جلب جذر الشجرة (لإلغاء الجذر)
    get_tree_root: false,

    // عرض اسم الجذر في الشجرة
    root_label: "Main Categories",

    // عناصر القائمة (Menu Items) - لإضافة عناصر جديدة
    menu_items: [
        {
            label: ("New Main Category"),
            action: function () {
                frappe.new_doc("Main Category", true);  // إنشاء فئة جديدة
            },
            condition: 'frappe.boot.user.can_create.indexOf("Main Category") !== -1',
        },
        {
            label: ("New Sub Category"),
            action: function () {
                frappe.new_doc("Sub Category", true);  // إنشاء تصنيف فرعي جديد
            },
            condition: 'frappe.boot.user.can_create.indexOf("Sub Category") !== -1',
        },
    ],

    // الحقول المطلوبة عند إضافة عقدة جديدة
    fields: [
        { 
            fieldtype: "Data", 
            fieldname: "category_name", 
            label: ("New Category Name"), 
            reqd: true 
        },
        {
            fieldtype: "Check",
            fieldname: "is_group",
            label: ("Is Group"),
            description: ("Categories under Groups can be expanded further.")
        },
        {
            fieldtype: "Data",
            fieldname: "category_number",
            label: ("Category Number"),
            description: __("Number of the new category, it will be included in the category name as a prefix")
        },
    ],

    // تجاهل بعض الحقول التي لا تريد عرضها
    ignore_fields: ["parent_main_category"],

    // عند تحميل الشجرة
    onload: function (treeview) {
        // يمكنك إضافة أزرار أو وظائف إضافية عند تحميل الشجرة
        console.log("Treeview loaded for Main Category");
    },

    // تخصيص إعدادات العرض (يمكنك عرض أي بيانات أخرى كما ترغب)
    get_tree_nodes: 'erpnext.main_category.get_children',

    // تعيين الدالة التي تُنفذ عند اختيار عقدة معينة
    click: function(node) {
        frappe.set_route("Form", "Main Category", node.label);
    },

    // تخصيص زر لإضافة عقدة جديدة
    extend_toolbar: true
};
