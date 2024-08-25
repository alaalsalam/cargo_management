frappe.ui.form.on('Cargo Shipment', {
	// TODO: Formatter for warehouse receipt item?
	create_invoice(frm) {
		if (frm.is_dirty()) {
			frappe.throw(__("Please Save First"));
			return;
		}
	
		let rows = frm.doc.cargo_shipment_lines.filter(i => !i.invoice);  // استخدام كل الصفوف التي لم تصدر فاتورة لها
		if (rows.length) {
			frappe.call({
				method: "cargo_management.shipment_management.doctype.cargo_shipment.cargo_shipment.create_purchase_invoice",
				args: {
					doc: frm.doc,
					rows: rows
				},
				callback: function(data) {
					frappe.set_route('Form', data.message.doctype, data.message.name);
				}
			});
		} else {
			frappe.msgprint(__("All Rows are Invoiced or No Rows Available!"));
		}
	},
	scan_barcode: function(frm) {
		if (!frm.doc.scan_barcode) {
			console.warn('No barcode entered.');
			return; // لا تكمل إذا كان الباركود فارغًا
		}
	
		frappe.call({
			method: 'check_barcode',
			doc: frm.doc,
			args: {
				barcode: frm.doc.scan_barcode,
			},
			callback: function(response) {
				console.log('Console API response:', response);
				if (response.message.success) {
					frappe.show_alert({ message: __("Parcel added successfully."), indicator: "green" });
					frm.refresh_field('cargo_shipment_lines'); // تحديث الحقل manifest_cargo_details
				} else {
					frappe.show_alert({ message: __("An error occurred: " + response.message.error), indicator: "red" });
				}
			},
			error: function(error) {
				console.error('Console API call error:', error);
				if (error.responseJSON) {
					console.error('Error details:', error.responseJSON);
					frappe.show_alert({ message: __("An error occurred while fetching Parcel details."), indicator: "red" });
				}
			}
		});

		var hideTimeout = 2000; 
        if (frm.doc.scan_barcode) {
            setTimeout(function() {
                frm.set_value('scan_barcode', '');
                frm.refresh_field('scan_barcode');
            }, hideTimeout);
        }

	},
	setup(frm) {
		frm.page.sidebar.toggle(false); // Hide Sidebar to better focus on the doc

		frm.set_indicator_formatter("package", function(doc) {
			return 'orange';
		});
	},

	onload(frm) {
		// Only packages on Warehouse Receipt
		frm.set_query('package', 'cargo_shipment_lines', () => {
		    return {
		        filters: {status: 'Awaiting Departure'}
		    }
		});
		frm.set_df_property('expected_arrival_date', 'reqd', true);


		frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Shipment Settings',
                fieldname: 'item'
            },
            callback: function(r) {
                if(r.message) {
                    let default_item = r.message.item;
                    
                    // التأكد من أن هناك سجلات في الجدول الفرعي
                    frm.doc.cargo_shipment_lines.forEach(function(item) {
                        if (!item.item) { // إذا كان الحقل فارغًا
                            item.item = default_item;
                        }
                    });
                    
                    frm.refresh_field('cargo_shipment_lines');
                }
            }
        });
	},


	refresh: function (frm) {
		// TODO: Add intro message when the cargo shipment is on a cargo shipment receipt
		// TODO: Add Progress: dashboard.add_progress or frappe.chart of type: percentage

		if (frm.is_new()) {
			return;
		}

		// frm.page.indicator.parent().append(cargo_management.transportation_indicator(frm.doc.transportation));

		frm.events.build_custom_action_items(frm);
		
		
		frappe.call({
			method: 'update_manifest_numbers',
			doc: frm.doc,
			callback: function(r) {
				if (r.message) {
					console.log(r.message.status);  // عرض حالة الاستجابة
					// frappe.show_alert({ message: __("Manifest numbers updated successfully."), indicator: "green" });
				} else {
					frappe.show_alert({ message: __("Failed to update manifest numbers."), indicator: "red" });
				}
			}
		});
	},

	validate: function (frm) {
		frm.doc.pieces = frm.doc.cargo_shipment_lines.length;

		frm.doc.estimated_gross_weight_by_warehouse_in_pounds = frm.get_sum('warehouse_lines', 'weight');
		frm.doc.estimated_gross_weight_by_carriers_in_pounds = frm.get_sum('cargo_shipment_lines', 'carrier_est_weight');
	},

	build_custom_action_items(frm) {
		if (frm.doc.status === 'Awaiting Departure') {
			frm.page.add_action_item(__('Confirm Packages'), () => {
				frappe.call({
					method: 'cargo_management.shipment_management.doctype.cargo_shipment.actions.update_status',
					freeze: true,
					args: {
						source_doc_name: frm.doc.name,
						new_status: 'Awaiting Departure',
						msg_title: __('Confirmed Packages')
					}
				});
			});

			frm.page.add_action_item(__('Confirm Transit'), () => {
				frappe.call({
					method: 'cargo_management.shipment_management.doctype.cargo_shipment.actions.update_status',
					freeze: true,
					args: {
						source_doc_name: frm.doc.name,
						new_status: 'In Transit',
						msg_title: __('Now in Transit')
					} // TODO: Refresh DOC in callback
				});
			});
		} else {
			frm.page.clear_actions_menu();
		}
	}
});


frappe.ui.form.on('Cargo Shipment Warehouse', {

	button: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		window.open('http://everest.cargotrack.net/m/track.asp?track=' + row.reference);
	}
});

// frappe.ui.form.on('Cargo Shipment Line', {
//     cargo_shipment_lines_add: function(frm, cdt, cdn) {
//         console.log("Row Added");

//         // Get the newly added row
//         let row = locals[cdt][cdn];

//         // Set the 'id' field to the document's name
//         row.parcel_id = frm.doc.name;

//         // Refresh the field to ensure it displays correctly
//         frm.refresh_field('cargo_shipment_lines');
//     }
// });
