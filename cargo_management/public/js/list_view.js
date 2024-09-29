frappe.provide("frappe.views");
console.log("##############frappe.views############################");
console.log("Custom List View script loaded");
console.log("##########################################");

// تأكد من أن الشيفرة تنتظر حتى يتم تحميل الصفحة بالكامل
// window.onload = function() {
//     if(cur_list.doctype){
//         console.log(cur_list.doctype)
//         add_list_button(cur_list.doctype)
//     }
// }
$(window).on('load', function() {
    const route2 = frappe.get_route();
    console.log(route2)
//     add_list_button(route2[1])
// });


// function add_list_button(doctype_name){
    // const route = frappe.get_route();
    // console.log(route)
    // if (route && route.length > 1) {
    //     const doctype = route[1]; // الحصول على اسم الشاشة من المسار
    //     console.log("Current doctype:", doctype);

    //     // تطبيق الإعدادات بناءً على الـ doctype الحالي
        frappe.listview_settings[route2[1]] = {
            onload: function(listview) {

                // if (listview && listview.cur_list) {
                //     console.log("Current doctype:", listview.cur_list.doctype);
                // } else {
                //     console.error("cur_list is not available");
                // }

                // console.log("ListView onload for doctype:", listview.doctype);
                listview.page.sidebar.toggle(false);  // إخفاء الشريط الجانبي
            },
            button: {
                show: () => true,
                get_label: () => __('Preview'),
                get_description: () => '',
                action(doc) {
                    if (doc) {
                        parcel_preview_dialog(doc);  // استدعاء الدالة
                    } else {
                        console.error("doc is not defined");
                    }
                }
            }
        };
    // } else {
    //     console.error("Route is not available or does not contain a doctype.");
    // }
});
// Parcel preview dialog function
function parcel_preview_dialog(doc) {
    console.log("Opening parcel preview dialog for doc:", doc);  // تأكيد استدعاء الدالة
    const preview_dialog = new frappe.ui.Dialog({
        title: 'General Overview',
        size: 'extra-large',
        fields: [
            { fieldtype: 'HTML', fieldname: 'preview' },
        ]
    });

    preview_dialog.show();
    
    preview_dialog.fields_dict.preview.$wrapper.html(`
        <div class="container">
            <h3 class="text-center">${doc.name}</h3>
            <div class="row">
                <div class="col-6">
                    <div class="card">
                        <div class="card-header">General Information</div>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">Shipper Name: <strong>${doc.name}</strong></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `);
}
