frappe.ui.form.on('Parcel', {
    refresh: function(frm) {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Shipment Settings',
                fieldname: 'commission'        
            },
            callback: function(r) {
                if (r.message && r.message.commission) {
                    let commission_type = r.message.commission;
                    
                    if (commission_type === 'From Warehouse') {
                        frm.set_df_property('commission_section', 'hidden', 1);
                    } else {
                        frm.set_df_property('commission_section', 'hidden', 0);
                        
                        frm.collapse_section('commission_section');
                    }
                } else {
                    frm.set_df_property('commission_section', 'hidden', 0);
                    
                    frm.collapse_section('commission_section');
                }
            }
        });
    },
	mode_of_payment: function(frm) {
		if (!frm.doc.company) {
			frappe.msgprint(__('Please enter the Company name.'));
			return;
		}
		if (frm.doc.mode_of_payment && frm.doc.company) {
			frappe.call({
				method: 'cargo_management.warehouse_management.doctype.warehouse_receipt.warehouse_receipt.get_account_for_mode_of_payment',
				args: {
					agent: frm.doc.mode_of_payment,
					company: frm.doc.company
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('receiving_account', r.message);
					}
				}
			});
		}
	},
});

frappe.ui.form.on('Parcel Content', {
	item_code: function(frm, cdt, cdn) {
		frm.trigger('calculate_commission');
		frm.trigger('calculate_shipping_amount');
	},
	
    amount: function(frm, cdt, cdn) {
		frm.trigger('calculate_commission');
		frm.trigger('calculate_total_amount');



	},
	rate: function(frm, cdt, cdn) {
		
		frm.trigger('calculate_shipping_amount');



	}
});
frappe.ui.form.on('Parcel Content', {
    item_code: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code) {
            frappe.call({
                method: "cargo_management.parcel_management.doctype.parcel.parcel.get_item_price",  // استدعاء دالة البايثون
                args: {
                    item_code: row.item_code
                },
                callback: function(r) {
                    if (r.message) {
                        // طباعة القيمة في رسالة

                        // تعيين السعر في الحقل
                        frappe.model.set_value(cdt, cdn, 'amount', r.message);
                    }
                }
            });
        }
    }
});
// دالة لاستدعاء دالة حساب shipping_amount عند إدخال Item_code
// frappe.ui.form.on('Parcel Content', {
//     item_code: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
        
//         // هنا يمكنك جلب الأبعاد بناءً على الـ Item_code
//         let length = row.length || 0;
//         let width = row.width || 0;
//         let height = row.height || 0;

       
//             // استدعاء دالة حساب الشحن
//             frappe.call({
//                 method: "cargo_management.parcel_management.doctype.parcel.parcel.calculate_shipping_amount",
//                 args: {
//                     length: length,
//                     width: width,
//                     height: height
//                 },
//                 callback: function(r) {
//                     if (r.message) {
// 						frappe.msgprint("The price of the item is: " );

//                         // تحديث حقل rate بناءً على النتيجة
//                         frappe.model.set_value(cdt, cdn, "rate", r.message);
//                     }
//                 }
//             });
//         }
//     }
// );

frappe.ui.form.on('Parcel', {
    not_arrived: function(frm) {
        if (frm.doc.not_arrived) {
            // إخفاء الحقول الأخرى عند تحديد not_arrived
            frm.toggle_display('returned_to_sender', false);
            frm.toggle_display('is_parcel_received', false);
        } else {
            // عرض الحقول مرة أخرى إذا لم يكن not_arrived محددًا
            frm.toggle_display('returned_to_sender', true);
            frm.toggle_display('is_parcel_received', true);
        }
    },
	
	returned_to_sender: function(frm) {
			if (frm.doc.returned_to_sender) {
				// إخفاء الحقول الأخرى عند تحديد not_arrived
				frm.toggle_display('not_arrived', false);
				frm.toggle_display('is_parcel_received', false);
			} else {
				// عرض الحقول مرة أخرى إذا لم يكن not_arrived محددًا
				frm.toggle_display('not_arrived', true);
				frm.toggle_display('is_parcel_received', true);
			}
		},
	is_parcel_received: function(frm) {
			if (frm.doc.is_parcel_received) {
				// إخفاء الحقول الأخرى عند تحديد not_arrived
				frm.toggle_display('returned_to_sender', false);
				frm.toggle_display('not_arrived', false);
			} else {
				// عرض الحقول مرة أخرى إذا لم يكن not_arrived محددًا
				frm.toggle_display('returned_to_sender', true);
				frm.toggle_display('not_arrived', true);
			}
		}

	
});
// 
frappe.ui.form.on('Parcel Content', {
	item_code: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		var item_code = row.item_code;
		var actual_weight = row.actual_weight; 
		var length = row.length || 0;
		var width = row.width || 0;
		var height = row.height || 0;
	
		// الوصول إلى parcel_price_rule من النموذج الرئيسي
		var parcel_price_rule = frm.doc.parcel_price_rule;
	
		// استخدام parcel_price_rule كقيمة افتراضية إذا لم يكن shipping_rule موجودًا
		var shipping_rule = row.shipping_rule || parcel_price_rule;
	
		// تعيين قيمة shipping_rule إذا لم يكن موجودًا
		if (!row.shipping_rule && parcel_price_rule) {
			frappe.model.set_value(cdt, cdn, 'shipping_rule', parcel_price_rule);
		}
	
		var amount = row.amount;
	
		frappe.call({
			method: 'cargo_management.parcel_management.doctype.parcel.parcel.calculate_shipping_amount_by_rule',
			args: {
				item_code: item_code,
				actual_weight: actual_weight,
				length: length,
				width: width,
				height: height,
				shipping_rule: shipping_rule,
				amount: amount,
			},
			callback: function(response) {
				if (response.message) {
					frappe.model.set_value(cdt, cdn, 'rate', response.message);
				} else {
					frappe.msgprint(__('No shipping amount found.'));
				}
			}
		});
	},
	shipping_rule: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		var item_code = row.item_code;
		var actual_weight = row.actual_weight; 
		var length = row.length || 0;
		var width = row.width || 0;
		var height = row.height || 0;
	
		// الوصول إلى parcel_price_rule من النموذج الرئيسي
		var parcel_price_rule = frm.doc.parcel_price_rule;
	
		var shipping_rule = row.shipping_rule || parcel_price_rule;
	
		// تعيين قيمة shipping_rule إذا لم يكن موجودًا
		if (!row.shipping_rule && parcel_price_rule) {
			frappe.model.set_value(cdt, cdn, 'shipping_rule', parcel_price_rule);
		}
	
		var amount = row.amount;
	
		frappe.call({
			method: 'cargo_management.parcel_management.doctype.parcel.parcel.calculate_shipping_amount_by_rule',
			args: {
				item_code: item_code,
				actual_weight: actual_weight,
				length: length,
				width: width,
				height: height,
				shipping_rule: shipping_rule,
				amount: amount,
			},
			callback: function(response) {
				if (response.message) {
					frappe.model.set_value(cdt, cdn, 'rate', response.message);
				} else {
					frappe.msgprint(__('No shipping amount found.'));
				}
			}
		});
	}
	
});

// frappe.ui.form.on('Parcel Content', {
//     qty: function(frm, cdt, cdn) {
//         calculate_amount(frm, cdt, cdn);
//     },
//     rate: function(frm, cdt, cdn) {
//         calculate_amount(frm, cdt, cdn);
//     }
// });

// function calculate_amount(frm, cdt, cdn) {
//     var row = locals[cdt][cdn];
//     if (row.qty && row.rate) {
//         row.amount = row.qty * row.rate;
//         frm.refresh_field('parcel_content'); // Refresh the table to show the updated value
//     }
// }



frappe.ui.form.on('Parcel', {

	create_invoice(frm) {
		if (frm.is_dirty()) {
			frappe.throw(__("Please Save First"));
			return;
		}
	
		let rows = frm.doc.content.filter(i => !i.invoice);  // استخدام كل الصفوف التي لم تصدر فاتورة لها
		if (rows.length) {
			frappe.call({
				method: "cargo_management.parcel_management.doctype.parcel.parcel.create_sales_invoice",
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
	before_save(frm) {
        if (frm.doc.status === "Draft") { // تحقق من حالة الوثيقة
            frm.set_value('status', 'Paid'); // تغيير الحالة إلى 'Paid'
        }
    },
	after_save(frm) {
        // استدعاء دالة بايثون للحصول على إعدادات "create_invoice"
        frappe.call({
            method: 'cargo_management.parcel_management.doctype.parcel.parcel.get_create_invoice_setting',  // مسار دالة بايثون
            callback: function(r) {
                let auto_create_invoice = r.message;
                
                if (auto_create_invoice === "Automatically") {
                    // تحديد الصفوف غير المفوترة
					let rows = frm.doc.content.filter(i => !i.invoice);  // استخدام كل الصفوف التي لم تصدر فاتورة لها
					if (rows.length) {
                        // استدعاء دالة لإنشاء الفاتورة
                        frappe.call({
                            method: "cargo_management.parcel_management.doctype.parcel.parcel.create_sales_invoice",
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
	setup(frm) {
	},

	onload(frm) {
		frm.page.sidebar.toggle(false);
		// FIXME: Observe if the indicator changes. This is useful for the 'Not Saved' status aka is_dirty(). We cannot read that from the events available
		const observer = new MutationObserver(() => {
			frm.layout.show_message('');     // Clear Message because it's possible that data changes!
			frm.page.clear_custom_actions(); // Clear Custom buttons
			frm.page.indicator.next().remove(); // Remove the extra indicator if the indicator changes
		});

		observer.observe(frm.page.indicator.get(0), {childList: true}); // Observe the 'indicator' for changes

		// Setting custom queries
		frm.set_query('item_code', 'content', () => {
			return {
				filters: {
					'is_sales_item': true,
					'has_variants': false
				}
			}
		});

		// Setting Currency Labels
		// frm.set_currency_labels(['total', 'shipping_amount'], 'USD');
		// frm.set_currency_labels(['rate', 'amount'], 'USD', 'content');
	
	},

	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.page.indicator.parent().append(cargo_management.transportation_indicator(frm.doc.transportation)); // Add Extra Indicator

		frappe.call({
            method: 'cargo_management.parcel_management.doctype.parcel.parcel.get_create_invoice_setting',  // مسار دالة بايثون
            callback: function(r) {
                let auto_create_invoice = r.message;
                
                if (auto_create_invoice === "Automatically") {
					frm.fields_dict['create_invoice'].wrapper.style.display = 'none';
				}}});
		// frm.events.show_explained_status(frm); // Show 'Explained Status' as Intro Message
		// frm.events.build_custom_actions(frm);  // Adding custom buttons
		
		//frm.trigger('parcel_preview_dialog');
	},

	tracking_number(frm) {
		frm.doc.tracking_number = frm.doc.tracking_number.trim().toUpperCase();  // Sanitize field

		if (!frm.doc.tracking_number) {
			return;
		}

		// frm.doc.carrier = cargo_management.find_carrier_by_tracking_number(frm.doc.tracking_number).carrier;

		refresh_many(['tracking_number', 'weight_type']);
	},

	shipping_amount(frm) {
		frm.events.calculate_total(frm);
	},
	
	// Custom Functions

	show_explained_status(frm) {
		frm.doc.explained_status.message.forEach(m => frm.layout.show_message(m, ''));  // FIXME: Core overrides color
		frm.layout.message.removeClass().addClass('form-message ' + frm.doc.explained_status.color);
	},
	build_custom_actions(frm) {
		// const carriers_settings = cargo_management.load_carrier_settings(frm.doc.carrier);

		// if (carriers_settings.api) {

		// if (frm.doc) { // If is Assisted Purchase will have related Sales Order and Sales Order Item
		// 	frm.add_custom_button(__('Sales Order'), () => frm.events.sales_order_dialog(frm), __('Get Items From'));
		// }

		frm.add_custom_button(__('Previwe'), () => frm.events.parcel_preview_dialog(frm));

		// carriers_settings.urls.forEach(url => frm.add_custom_button(url.title, () => window.open(url.url + frm.doc.tracking_number)));
	},

	parcel_preview_dialog(frm) {
		const preview_dialog = new frappe.ui.Dialog({
			title: 'General Overview', size: 'extra-large',
			fields: [
				{fieldtype: 'HTML', fieldname: 'preview'},
			]
		});

		preview_dialog.show()
		// <h3 class="text-center">${frm.doc.carrier} - ${frm.doc.tracking_number} ${cargo_management.transportation_indicator(frm.doc.transportation)}</h3>

		preview_dialog.fields_dict.preview.$wrapper.html(`
		<div class="container">
			<h3 class="text-center">${frm.doc.tracking_number} -${frm.doc.destination}</h3>

			<div class="row">
				<div class="col-6">
					<div class="card">
						<div class="card-header">General Information</div>
						<ul class="list-group list-group-flush">
							<li class="list-group-item">Shipper Name: <strong>${frm.doc.shipper_name}</strong></li>
							<li class="list-group-item">Receiver Name: <strong>${frm.doc.receiver_name}</strong></li>
							<li class="list-group-item">Destination : <strong>${frm.doc.destination}</strong></li>
						</ul>
					</div>
				</div>
				<div class="col-6">
					<div class="card">
						<div class="card-header">Descripcion</div>
						<ul class="list-group list-group-flush">
							${frm.doc.content.map((c) => {
								return (`<li class="list-group-item">Descripcion: <strong>${c.description}</strong> | Tracking: <strong>${c.tracking_number}</strong></li>`);
							}).join('') }
						</ul>
					</div>
				</div>
			</div>
			<div class="flex-row justify-content-between align-items-start border rounded p-3 my-3">
						<div class="card">
						<div class="card-header">Note</div>
						<ul class="list-group list-group-flush">
							<li class="list-group-item">Additional Notes: <strong>${frm.doc.notes}</strong></li>
						</ul>
					</div>
				</div>
			</div>
			<div class="d-flex flex-row justify-content-between align-items-start border rounded p-3 my-3">
				<div>
					<div class="mb-2"><span class="badge badge-primary">Order Date</span> <strong>${frm.doc.order_date}</strong></div>
				</div>
				<div class="d-flex flex-column">
					<div class="mb-2"><span class="badge badge-secondary">Estimated Delivery Date (Earliest) 1</span> <strong>${frm.doc.est_delivery_1}</strong></div>
					<div><span class="badge badge-secondary">Estimated Delivery Date (Latest) 2</span> <strong>${frm.doc.est_delivery_2}</strong></div>
				</div>
				<div>
					<div><span class="badge badge-success">Estimated Departure Date</span> <strong>${frm.doc.est_departure}</strong></div>
				</div>
				<div>
					<div><span class="badge badge-success">Carrier estimated delivery date</span> <strong>${frm.doc.est_departure}</strong></div>
				</div>
			</div>

		</div>`);

	},
	refresh: function(frm) {
		// Trigger necessary events on form refresh
		// frm.events.transportation_multi_check(frm);
		frm.events.show_general_ledger(frm);
		erpnext.accounts.ledger_preview.show_accounting_ledger_preview(frm);
	},
	
	show_general_ledger: function (frm) {
		// Ensure the button only shows if the document status is greater than 0 (submitted or cancelled)
		if (frm.doc.docstatus > 0) {
			// Add the "Ledger" button
			frm.add_custom_button(
				__("Ledger"),
				function () {
					frappe.route_options = {
						voucher_no: frm.doc.name,
						from_date: frm.doc.order_date,
						to_date: moment(frm.doc.modified).format("YYYY-MM-DD"),
						company: frm.doc.company,
						group_by: "",
						show_cancelled_entries: frm.doc.docstatus === 2,  // Show cancelled entries if the document is cancelled
					};
					frappe.set_route("query-report", "General Ledger");
				},
				"fa fa-table"  // Optional icon for the button
			);
		}
	},

	get_rate_commission :function (frm){
		frappe.call({
			method: 'cargo_management.warehouse_management.doctype.warehouse_receipt.warehouse_receipt.get_rate_for_agent',
			args: {
				agent: frm.doc.agent,
			},
			callback: function(r) {
				if (r.message) {
					frm.set_value('commission_rate', r.message); 
				}
			}
		});
	},

	agent :function(frm){
		if (frm.doc.agent && frm.doc.company) {
			frappe.call({
				method: 'cargo_management.warehouse_management.doctype.warehouse_receipt.warehouse_receipt.get_account_for_company',
				args: {
					agent: frm.doc.agent,
					company: frm.doc.company,
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('agent_account', r.message);  
					}
				}
			});
		
		//###############
		frm.trigger('get_rate_commission');

	
		frm.trigger('calculate_total_amount');
		frm.trigger('calculate_shipping_amount');

	}},

	
	calculate_commission: function (frm) {
		let section = frm.fields_dict.commission_section;
		if (section && section.df.hidden) {
			// إذا كان مخفيًا، تعيين العمولة إلى 0 وعدم المتابعة في الحساب
			frm.set_value('total_commission', 0);
			return;
		}
	
	
        if (!frm.doc.commission_rate || frm.doc.commission_rate === 0) {
            frm.set_value('total_commission', 0);
            return;
        }
        frappe.call({
            method: 'cargo_management.warehouse_management.doctype.warehouse_receipt.warehouse_receipt.calculate_commission',
            args: {
                total: frm.doc.total,
                commission_rate: frm.doc.commission_rate
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value('total_commission', r.message);
                } else {
                    frm.set_value('total_commission', 0);
                }
                console.log('Total Commission:', frm.doc.total_commission);
            }
        });
    },
	total_commission: function(frm) {
        frm.trigger('calculate_rate_from_commission');
    },
	calculate_rate_from_commission: function(frm) {
		if (!frm.doc.total) {
			// frappe.msgprint(__('Please enter the total amount before calculating the commission rate.'));
			return;
		}
        frappe.call({
            method: 'cargo_management.warehouse_management.doctype.warehouse_receipt.warehouse_receipt.calculate_rate',
            args: {
                total: frm.doc.total,
                total_commission: frm.doc.total_commission
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value('commission_rate', r.message);
                }
            }
        });
    },
	calculate_total_amount: function (frm) {
        let total_amount = 0;
        if (frm.doc.content.length > 0) {
            frm.doc.content.forEach(function (row) {
                total_amount += row.amount;
            });
        }
	
		frm.set_value('total', total_amount);
		frm.trigger('calculate_commission');

       // console.log('Total Shipment Amount:', total_amount);
       // frm.trigger('calculate_commission'); // Call calculate_commission only once
    },
	calculate_shipping_amount: function (frm) {
		let shipping_amount = 0;
		if (frm.doc.content.length > 0) {
			frm.doc.content.forEach(function (row) {
				shipping_amount += row.rate;
			});
		} frm.set_value('shipping_amount', shipping_amount);
		console.log("hi ");
	},
	
	total_commission: function(frm) {
        frm.trigger('calculate_rate_from_commission');
    },
	commission_rate : function(frm) {
		frm.trigger('calculate_commission');
	},
	shipper_name : function(frm){
			if (frm.doc.shipper_name && frm.doc.company) {
				frappe.call({
					method: 'cargo_management.parcel_management.doctype.parcel.parcel.get_account_for_customer',
					args: {
						agent: frm.doc.shipper_name,
						company: frm.doc.company,
					},
					callback: function(r) {
						if (r.message) {
							frm.set_value('debit_to', r.message);  
						}
					}
				});
			}
	},
	
	est_departure: function(frm) {
		var selected_date = frm.doc.est_departure;
		var today = frappe.datetime.get_today();
		
		if (selected_date < today) {
			frappe.msgprint(__('The departure date cannot be earlier than today.'));
			frappe.validated = false; 
			frm.set_value('est_departure', null); 		}
	},
	est_delivery_1: function(frm) {
        var selected_delivery = frm.doc.est_delivery_1;
        var selected_departure = frm.doc.est_departure;

        if (selected_delivery < frappe.datetime.get_today()) {
            frappe.msgprint(__('The departure date cannot be earlier than today.'));
            frappe.validated = false; 
            frm.set_value('est_delivery_1', null);
        } else if (selected_departure && selected_delivery < selected_departure) {
            frappe.msgprint(__('The delivery date must be greater than or equal to the departure date.'));
            frappe.validated = false;
            frm.set_value('est_delivery_1', null);
        }
    },
	est_delivery_2: function(frm) {
        var selected_delivery = frm.doc.est_delivery_2;
        var selected_departure = frm.doc.est_departure;

        if (selected_delivery < frappe.datetime.get_today()) {
            frappe.msgprint(__('The departure date cannot be earlier than today.'));
            frappe.validated = false; 
            frm.set_value('est_delivery_2', null);
        } else if (selected_departure && selected_delivery < selected_departure) {
            frappe.msgprint(__('The delivery date must be greater than or equal to the departure date.'));
            frappe.validated = false; 
            frm.set_value('est_delivery_2', null); 
        }
    },

	
	// shipper_name : function (frm){
	// 	erpnext.utils.get_party_details(
	// 		this.frm,
	// 		"erpnext.accounts.party.get_party_details",
	// 		{
	// 			posting_date: this.frm.doc.order_date,
	// 			party: this.frm.doc.shipper_name,
	// 			party_type: "Customer",
	// 			account: this.frm.doc.debit_to,
	// 			// price_list: this.frm.doc.selling_price_list,
	// 			// pos_profile: pos_profile,
	// 		},
	// 		// function () {
	// 		// 	me.apply_pricing_rule();
	// 		// }
	// 	);
	// },
	
	//https://github.com/frappe/frappe/pull/12471 and https://github.com/frappe/frappe/pull/14181/files
	// sales_order_dialog(frm) {
	// 	const so_dialog = new frappe.ui.form.MultiSelectDialog({
	// 		doctype: 'Sales Order',
	// 		target: frm,
	// 		setters: {
	// 			delivery_date: undefined,
	// 			status: undefined
	// 		},
	// 		add_filters_group: 1,
	// 		get_query: () => {
	// 			return {
	// 				filters: {  // TODO: Only uncompleted orders!
	// 					docstatus: 1,
	// 					customer: frm.doc.customer,
	// 				}
	// 			};
	// 		},
	// 		action: (selections) => {
	// 			if (selections.length === 0) {
	// 				frappe.msgprint(__("Please select {0}", [so_dialog.doctype]))
	// 				return;
	// 			}
	// 			// so_dialog.dialog.hide();
	// 			frm.events.so_items_dialog(frm, selections);
	// 		}
	// 	});
	// },

	so_items_dialog: async function (frm, sales_orders) {
		// Getting all sales order items from Sales Order
		let sale_order_items = await frappe.db.get_list('Sales Order Item', {
			filters: {'parent': ['in', sales_orders]},
			fields: ['name as docname', 'item_code', 'description', 'qty', 'rate']
		});

		const so_items_dialog = new frappe.ui.form.MultiSelectDialog({
			doctype: 'Sales Order Item',
			target: frm,
			setters: {
				// item_code: undefined,
				// qty: undefined,
				// rate: undefined
			},
			data_fields: [
				{
					fieldtype: 'Currency',
					options: "USD",
					fieldname: "rate",
					read_only: 1,
					hidden: 1,
				},
				{
					fieldname: 'item_code',
					fieldtype: 'Data',
					label: __('Item sshhshsh')
				}],
			get_query: () => {
				return {
					filters: {
						parent: ['in', sales_orders]
					}
				}
			},
			add_filters_group: 1,
			action: (jkjk) => {
				console.log(jkjk);
			},
			primary_action_label: __('Select')
		});

	},

	calculate_total(frm) {
		frm.trigger('calculate_total_amount');
		frm.trigger('calculate_shipping_amount');


		//Sfrm.set_value('total', frm.get_sum('content', 'amount') + frm.doc.shipping_amount);
		frm.set_value('total_actual_weight', frm.get_sum('content', 'actual_weight'));
		frm.set_value('total_volumetric_weight', frm.get_sum('content', 'volumetric_weight'));
		frm.set_value('total_net_length', frm.get_sum('content', 'length'));
		frm.set_value('total_net_width', frm.get_sum('content', 'width'));
		frm.set_value('total_net_height', frm.get_sum('content', 'height'));
		frm.set_value('total_qty', frm.get_sum('content', 'qty'));
		if(frm.doc.total_volumetric_weight > frm.doc.total_actual_weight){
			frm.set_value('weight_type', 'Volumetric Weight');
		}
		else{
			frm.set_value('weight_type', 'Actual Weight');
		}
	},
	calculate_content_amounts_and_total(frm, cdt, cdn) {
		console.log("--------calculate_content_amounts_and_total------")
		let row = locals[cdt][cdn]; // Getting Content Child Row being edited

		// row.amount = row.qty * row.rate;
		row.volumetric_weight = (row.length * row.width * row.height) / 1000000;
		refresh_field('amount', cdn, 'content');

		frm.events.calculate_total(frm); // Calculate the parent 'total' field
	},
	// parcel_price_rule(frm) {
	// 	if(frm.doc.parcel_price_rule) {
	// 		return frm.call({
	// 			doc: frm.doc,
	// 			method: "apply_parcel_price_rule",
	// 			callback: function(r) {
	// 				calculate_content_amounts_and_total();
	// 			}
	// 		}).fail(() => frm.set_value('parcel_price_rule', ''));
	// 	}
	// }
	
});

frappe.ui.form.on('Parcel Content', {

	content_remove(frm) {
		frm.events.calculate_total(frm);
	},

	qty(frm, cdt, cdn) {
		frm.events.calculate_content_amounts_and_total(frm, cdt, cdn);
	},

	rate(frm, cdt, cdn) {
		frm.events.calculate_content_amounts_and_total(frm, cdt, cdn);
	},
	actual_weight(frm, cdt, cdn) {
		frm.events.calculate_content_amounts_and_total(frm, cdt, cdn);
	},
	volumetric_weight(frm, cdt, cdn) {
		frm.events.calculate_content_amounts_and_total(frm, cdt, cdn);
	},
	length(frm, cdt, cdn) {
		frm.events.calculate_content_amounts_and_total(frm, cdt, cdn);
	},
	width(frm, cdt, cdn) {
		frm.events.calculate_content_amounts_and_total(frm, cdt, cdn);
	},
	height(frm, cdt, cdn) {
		frm.events.calculate_content_amounts_and_total(frm, cdt, cdn);
	},


});
