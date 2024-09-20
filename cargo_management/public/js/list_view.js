console.log("##########################################");
console.log("Custom List View script loaded");
console.log("##########################################");

// الحصول على المسار الحالي
const route = frappe.get_route();
console.log("Current route:", route);


// تحقق من أن المسار يحتوي على العناصر الصحيحة
// if (route && route.length > 1) {
//     console.log("Current doctype:", route[1]);  // طباعة اسم الدوك تايب
// } else {
//     console.error("Route is not available or does not contain a doctype.");
// }

// تعيين إعدادات قائمة العرض لكل دوك تايب
// frappe.listview_settings['*'] = {
//     onload: function(listview) {
//         if (this.cur_list) {
//             console.log("Current doctype:", this.cur_list.doctype);
//         } else {
//             console.error("cur_list is not available");
//         }

//         console.log("ListView onload for doctype:", listview.doctype);
//         listview.page.sidebar.toggle(false);  // إخفاء الشريط الجانبي
//     },
//     button: {
//         show: () => true,
//         get_label: () => __('Preview'),
//         get_description: () => '',
//         action(doc) {
//             // تأكد من أن doc موجود هنا
//             if (doc) {
//                 parcel_preview_dialog(doc);  // استدعاء الدالة
//             } else {
//                 console.error("doc is not defined");
//             }
//         }
//     }
// };

// function parcel_preview_dialog(doc) {
//     console.log("Opening parcel preview dialog for doc:", doc);  // تأكيد استدعاء الدالة
//     const preview_dialog = new frappe.ui.Dialog({
//         title: 'General Overview',
//         size: 'extra-large',
//         fields: [
//             { fieldtype: 'HTML', fieldname: 'preview' },
//         ]
//     });

//     preview_dialog.show();
    
//     preview_dialog.fields_dict.preview.$wrapper.html(`
//         <div class="container">
//             <h3 class="text-center">${doc.name}</h3>
//             <div class="row">
//                 <div class="col-6">
//                     <div class="card">
//                         <div class="card-header">General Information</div>
//                         <ul class="list-group list-group-flush">
//                             <li class="list-group-item">Shipper Name: <strong>${doc.name}</strong></li>
//                         </ul>
//                     </div>
//                 </div>
//             </div>
//         </div>`);
// }