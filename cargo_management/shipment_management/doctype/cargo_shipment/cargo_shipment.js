frappe.ui.form.on('Cargo Shipment', {
	refresh: function(frm) {
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Shipment Settings',
				fieldname: ['in_customs', 'in_transit']  
			},
			callback: function(r) {
				if (r.message) {
					let in_customs = parseInt(r.message.in_customs);  
					let in_transit = parseInt(r.message.in_transit);  
		
					console.log("in_customs value:", in_customs);
					console.log("in_transit value:", in_transit);
		
					
					frm.toggle_display('customs_information_section', in_customs !== 0);
		
					
					frm.toggle_display('transit_information_section', in_transit !== 0);
				} else {
					console.error("Failed to retrieve in_customs or in_transit values.");
				}
			}
		});
		
	
	
		
		let state = frm.doc.workflow_state;
		let progress = 0;
		
		if (state === 'Awaiting Departure') {
			progress = 25;
		} else if (state === 'In Transit') {
			progress = 50;
		} else if (state === 'Sorting') {
			progress = 75;
		} else if (state === 'Finished') {
			progress = 100;
		}

		frm.dashboard.add_progress('Shipment Progress', progress);


	}
});

frappe.ui.form.on('Cargo Shipment', {


	// refresh: function(frm) {
        
    //     frappe.call({
    //         method: 'frappe.client.get_value',
    //         args: {
    //             doctype: 'Shipment Settings',
    //             fieldname: 'in_customs'
    //         },
    //         callback: function(r) {
    //             if (r.message) {
    //                 let in_customs = r.message.in_customs;
	// 				console.log("in_customs");
    //                 // let in_transit = r.message.in_transit;

                    
    //                 if (in_customs === 0) {
    //                     frm.set_df_property('customs_information_section', 'hidden', 1);  
    //                 } else {
    //                     frm.set_df_property('customs_information_section', 'hidden', 0);  
	// 					frm.collapse_section('customs_information_section');

    //                 }

                    
    //                 // if (in_transit === 0) {
    //                 //     frm.set_df_property('transit_information_tab', 'hidden', 1);  
    //                 // } else {
    //                 //     frm.set_df_property('transit_information_tab', 'hidden', 0); 
    //                 // }
    //             }
	// 		}
    //     });

	// 	// frappe.call({
    //     //     method: 'frappe.client.get_value',
    //     //     args: {
    //     //         doctype: 'Shipment Settings',
    //     //         fieldname: 'commission'        
    //     //     },
    //     //     callback: function(r) {
    //     //         if (r.message && r.message.commission) {
    //     //             let commission_type = r.message.commission;
                    
    //     //             if (commission_type === 'From Warehouse') {
    //     //                 frm.set_df_property('commission_section', 'hidden', 1);
    //     //             } else {
    //     //                 frm.set_df_property('commission_section', 'hidden', 0);
                        
    //     //                 frm.collapse_section('commission_section');
    //     //             }
    //     //         } else {
    //     //             frm.set_df_property('commission_section', 'hidden', 0);
                    
    //     //             frm.collapse_section('commission_section');
    //     //         }
    //     //     }
    //     // });
	// },



	create_invoice: function(frm) {
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

	after_save: function(frm) {
		// استدعاء دالة بايثون للحصول على إعدادات "create_invoice"
		frappe.call({
			method: 'cargo_management.parcel_management.doctype.parcel.parcel.get_create_invoice_setting',
			callback: function(r) {
				let auto_create_invoice = r.message;

				if (auto_create_invoice === "Automatically") {
					console.log(auto_create_invoice);
					// تحديد الصفوف غير المفوترة
					let rows = frm.doc.cargo_shipment_lines.filter(i => !i.invoice);
					if (rows.length) {
						// استدعاء دالة لإنشاء الفاتورة
						frappe.call({
							method: "cargo_management.shipment_management.doctype.cargo_shipment.cargo_shipment.create_purchase_invoice",
							args: {
								doc: frm.doc,
								rows: rows
							},
							callback: function(data) {
								frappe.set_route('Form', data.message.doctype, data.message.name);
							},
							error: function(err) {
								console.error(__('Error: {0}').format(err.responseText));
							}
						});
					}
				}
			},
			error: function(err) {
				console.error(__('Error: {0}').format(err.responseText));
			}
		});
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

	setup: function(frm) {
		frm.page.sidebar.toggle(false); // Hide Sidebar to better focus on the doc

		frm.set_indicator_formatter("package", function(doc) {
			return 'orange';
		});
	},

	onload: function(frm) {
		
		// Only packages on Warehouse Receipt
		frm.set_query('package', 'cargo_shipment_lines', () => {
			return {
				filters: {status: 'Awaiting Departure', transportation: frm.doc.transportation}
			};
		});
		frm.set_df_property('expected_arrival_date', 'reqd', true);

		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Shipment Settings',
				fieldname: 'item'
			},
			callback: function(r) {
				if (r.message) {
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

	refresh: function(frm) {
		frm.fields_dict['warehouse_lines'].grid.get_field('reference').get_query = function() {
			return {
				filters: { 'status': 'Available' }  // مثال على فلترة المخازن
			};
		};
	},

	warehouse_lines_add: function(frm, cdt, cdn) {
		// عند إضافة مخزن جديد
		update_parcels(frm);

		if (frm.is_new()) {
			return;
		}

		frm.events.build_custom_action_items(frm);

		frappe.call({
			method: 'update_manifest_numbers',
			doc: frm.doc,
			callback: function(r) {
				if (r.message) {
					console.log(r.message.status);  // عرض حالة الاستجابة
				}
			}
		});

		frappe.call({
			method: 'update_parcel_status',
			args: {
				cargo_shipment_name: frm.doc.name
			},
			callback: function(response) {
				if (response.message) {
					frappe.msgprint(__('Parcel statuses updated successfully.'));
				} else {
					frappe.show_alert({ message: __("Failed to update parcel_status."), indicator: "red" });
				}
			}
		});

		frappe.call({
			method: 'cargo_management.parcel_management.doctype.parcel.parcel.get_create_invoice_setting',
			callback: function(r) {
				let auto_create_invoice = r.message;

				if (auto_create_invoice === "Automatically") {
					frm.fields_dict['create_invoice'].wrapper.style.display = 'none';
				}
			}
		});
	},

	validate: function(frm) {
		frm.doc.pieces = frm.doc.cargo_shipment_lines.length;

		frm.doc.estimated_gross_weight_by_warehouse_in_pounds = frm.get_sum('warehouse_lines', 'weight');
		frm.doc.estimated_gross_weight_by_carriers_in_pounds = frm.get_sum('cargo_shipment_lines', 'carrier_est_weight');
	},

	build_custom_action_items: function(frm) {
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
					}
				});
			});
		} else {
			frm.page.clear_actions_menu();
		}
	}
});

frappe.ui.form.on('Cargo Shipment Warehouse', {
	button: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		window.open('http://everest.cargotrack.net/m/track.asp?track=' + row.reference);
	}
});

frappe.ui.form.on('Cargo Shipment Line', {
	cargo_shipment_lines_add: function(frm, cdt, cdn) {
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Item',
				fieldname: 'description',
				filters: { name: frm.doc.item }
			},
			callback: function(r) {
				if (r.message) {
					let row = frappe.model.get_doc(cdt, cdn);
					row.description = r.message.description;
					frm.refresh_field('cargo_shipment_lines');
				}
			}
		});
	}
});
