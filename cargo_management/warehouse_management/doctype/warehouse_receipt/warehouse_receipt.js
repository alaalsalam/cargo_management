frappe.ui.form.on('Warehouse Receipt', {
	agent_account: function (frm) {
		if (frm.set_party_account_based_on_party) return;
	
		frm.events.set_account_currency_and_balance(
			frm,
			frm.doc.agent_account,
			"paid_from_account_currency",
			"paid_from_account_balance",
			function (frm) {
				frm.events.total_shipment_amount(frm); 
			}
		);
	},
	paid_to: function (frm) {
		if (frm.set_party_account_based_on_party) return;

		frm.events.set_account_currency_and_balance(
			frm,
			frm.doc.paid_to,
			"paid_to_account_currency",
			"paid_to_account_balance",
			function (frm) {
					if (frm.doc.paid_from_account_currency == frm.doc.paid_to_account_currency) {
						if (frm.doc.source_exchange_rate) {
							frm.set_value("	", frm.doc.source_exchange_rate);
						}
						frm.set_value("received_amount", frm.doc.total_shipment_amount);
					} else {
						frm.events.received_amount(frm);
					}
				
			}
		);
	},
	set_account_currency_and_balance: function (
		frm,
		account,
		currency_field,
		balance_field,
		callback_function
	) {
		var company_currency = frappe.get_doc(":Company", frm.doc.company).default_currency;
		if (frm.doc.posting_date && account) {
			frappe.call({
				method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_account_details",
				args: {
					account: account,
					date: frm.doc.posting_date,
					cost_center: frm.doc.cost_center,
				},
				callback: function (r, rt) {
					if (r.message) {
						frappe.run_serially([
							() => frm.set_value(currency_field, r.message["account_currency"]),
							() => {
								frm.set_value(balance_field, r.message["account_balance"]);
	
								if (
									frm.doc.paid_from_account_currency ==
										frm.doc.paid_to_account_currency &&
									frm.doc.total_shipment_amount != frm.doc.received_amount
								) {
									if (
										company_currency != frm.doc.paid_from_account_currency
									) {
										frm.doc.total_shipment_amount = frm.doc.received_amount;
									}
								}
							},
							() => {
								if (callback_function) callback_function(frm);
	
							// 	frm.events.hide_unhide_fields(frm);
							// 	frm.events.set_dynamic_labels(frm);
							},
						]);
					}
				},
			});
		}
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
						frm.set_value('paid_to', r.message);
					}
				}
			});
		}
	},	
	transportation_multi_check: function (frm) {
		console.log("--------transportation_multi_check---------")
		frm.transportation = frappe.ui.form.make_control({
			parent: frm.fields_dict.transportation_multicheck_html.$wrapper.addClass('text-center'),
			render_input: true,
			df: {
				placeholder: __('Select item group'),
				fieldname: 'transportation_options',
				fieldtype: 'MultiCheckSingle',
				label: __('Transportation'),
				reqd: true, bold: true, columns: 2,
				options: [{label: __('SEA'), value: 'Sea'}, {label: __('AIR'), value: 'Air', description: 'Air'}],
				on_change: (selected) => frm.doc.transportation = selected
			}
		});

	},

	refresh: function(frm) {
		frm.events.transportation_multi_check(frm);
		frm.events.show_general_ledger(frm);
		erpnext.accounts.ledger_preview.show_accounting_ledger_preview(frm);
    },
    calculate_total_amount: function (frm) {
        let total_amount = 0;
        frm.doc.child_table_fieldname.forEach(function (row) {
            total_amount += row.amount || 0;
        });
        frm.set_value('total_shipment_amount', total_amount);
    },
	show_general_ledger: function (frm) {
		if (frm.doc.docstatus > 0) {
			frm.add_custom_button(
				__("Ledger"),
				function () {
					frappe.route_options = {
						voucher_no: frm.doc.name,
						from_date: frm.doc.posting_date,
						to_date: moment(frm.doc.modified).format("YYYY-MM-DD"),
						company: frm.doc.company,
						group_by: "",
						show_cancelled_entries: frm.doc.docstatus === 2,
					};
					frappe.set_route("query-report", "General Ledger");
				},
				"fa fa-table"
			);
		}
	},
	setup: function (frm) {
		
		frm.page.sidebar.toggle(false); // Hide Sidebar

		if (frm.is_new())
			frm.events.transportation_multi_check(frm);
		frm.set_query("paid_to", function() {
            return {
                filters: {
                    account_type: ["in", ["Bank", "Cash"]],
                    is_group: 0,
                    company: frm.doc.company
                }
            };

		});
		frm.set_query("agent_account", function() {
            return {
                filters: {
                    account_type: ["in", ["Receivable"]],
                    is_group: 0,
                    company: frm.doc.company
                }
            };

		});
	},

	onload_post_render: function (frm) {},

	before_save: function (frm) {
		calculate_total_amount_and_update_paid(frm);
	},

	after_save: function (frm) {},

	tracking_number: function (frm) {
		frm.doc.tracking_number = frm.doc.tracking_number.trim().toUpperCase();

		if (!frm.doc.tracking_number) {
			return;
		}

		frappe.call({
			method: 'cargo_management.warehouse_customization.doctype.warehouse_receipt.actions.find_package_by_tracking_number',
			type: 'GET',
			freeze: true,
			freeze_message: __('Searching Package...'),
			args: {tracking_number: frm.doc.tracking_number},
			callback: (r) => { // TODO: Maybe a Switch
				if (r.message.coincidences) {
					frm.events.show_selector_dialog(frm, r.message);
				} else if (r.message.coincidence) {
					frappe.show_alert('Paquete Pre-Alertado.');
					frm.events.set_package(frm, r.message.coincidence);
				} else {
					frappe.show_alert('Paquete sin Pre-Alerta.');
				}
			}
		});

	},

	// Custom Functions
	show_selector_dialog: function (frm, opts) {
		// https://frappeframework.com/docs/v13/user/en/api/controls & https://frappeframework.com/docs/v13/user/en/api/dialog
		// MultiselectDialog with Package List -> Issue: can select multiple
		// Dialog with a Table Field of Package List -> Issue: can select multiple and needs a select button
		// MultiCheck Field with Package List as Options -> Issue: can select multiple. No extra data for package identification
		// Select Field with Package List as Options -> Issue: Small extra data for package identification, and need a select button or event trigger.
		// LinkSelector with Package List as Options -> Issue: its exactly what we need. But without search and button and configurable extra fields

		const selector_dialog = new frappe.ui.Dialog({
			title: __('Coincidences found for: {0}', [frm.doc.tracking_number]),
			static: true,          // Cannot cancel touching outside pop-up
			no_cancel_flag: true,  // Cannot cancel with keyboard
			size: 'extra-large',
			fields: [{fieldtype: 'HTML', fieldname: 'table_html'}]
		});

		selector_dialog.fields_dict.table_html.$wrapper
			.html(frappe.render_template('package_selector', {
				search_term: opts.search_term,
				coincidences: opts.coincidences
			}))
			.find('a').on('click', e => {
			e.preventDefault();
			selector_dialog.hide();
			frm.events.set_package(frm, $(e.target).attr('data-value'));
		});

		selector_dialog.show();
	},

	set_package: function (frm, coincidence) {
		const doc_name = coincidence.name || coincidence;

		frappe.db.get_doc('Package', doc_name).then(doc => {
			frm.doc.tracking_number = doc.name;
			frm.doc.carrier = doc.carrier;

			frm.transportation.$checkbox_area.find(`:checkbox[data-unit="${doc.transportation}"]`).trigger('click'); // This Trigger on_change

			// FIXME: Join this fields?
			frm.doc.shipper = doc.shipper;
			frm.doc.consignee = doc.customer_name;

			frm.doc.customer_description = (doc.content.length > 0) ? doc.content.map(c => 'Item: ' + c.description + '\nCantidad: ' + c.qty).join("\n\n") : null;

			frm.refresh_fields();
			frm.events.show_alerts(frm); // FIXME: Work on this
		});
	},
	agent: function(frm) {
		frm.set_value('commission_rate', '');
		frm.set_value('total_commission', '');

	
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
		}
	
		if (!frm.doc.agent) {
			return;
		}
	
		fetch_packages_by_agent_and_transportation(frm);
	
		if (frm.doc.posting_date) {
			frappe.call({
				method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_party_and_account_balance",
				args: {
					company: frm.doc.company,
					date: frm.doc.posting_date,
					paid_from: frm.doc.agent_account,
					paid_to: frm.doc.paid_to,
					ptype: "Agent",
					pty: frm.doc.agent,
					cost_center: frm.doc.cost_center,
				},
				callback: function (r) {
					if (r.message) {
						frm.set_value("paid_from_account_balance", r.message.paid_from_account_balance);
						frm.set_value("paid_to_account_balance", r.message.paid_to_account_balance);
						frm.set_value("party_balance", r.message.party_balance);
					}
				}
			});
		}
	
		frm.set_value('total_shipment_amount', '');
	
		frappe.run_serially([
			() => {
				return new Promise((resolve) => {
					setTimeout(resolve, 500);  // تأخير لتحديث الحزم
				});
			},
			() => frappe.call({
				method: 'calculate_total_amount',
				doc: frm.doc,
				callback: function(r) {
					if (r.message) {
						frm.set_value('total_shipment_amount', r.message);
					} else {
						console.log("Error calculating total amount.");
					}
				}
			})
		]).then(() => {
			// حساب العمولة بعد تحديث إجمالي الشحنة
			frappe.call({
				method: 'cargo_management.warehouse_management.doctype.warehouse_receipt.warehouse_receipt.calculate_commission',
				args: {
					total: frm.doc.total_shipment_amount,
					commission_rate: frm.doc.commission_rate
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('total_commission', r.message);
					}
				}
			});
		});
		
	},
	
    transportation: function(frm) {
        if (!frm.doc.agent) {
            return;
        }
        fetch_packages_by_agent_and_transportation(frm);
    },
	show_alerts: function(frm) {
		// TODO: Make this come from API?
		frm.dashboard.clear_headline();

		if (frm.doc.customer_description) {
			frm.layout.show_message('<b>No es necesario abrir el paquete. <br> Cliente Pre-Alerto el contenido.</b>', '');
			frm.layout.message.removeClass().addClass('form-message ' + 'green');  // FIXME: Core overrides color
		}
	},
	onload: function(frm){
		let today = frappe.datetime.nowdate();  // الحصول على تاريخ اليوم
        frm.set_value('posting_date', today); 
	}	
});
function fetch_packages_by_agent_and_transportation(frm) {
    // نزيل بيانات الجدول الحالية لتجنب التكرار
    frm.clear_table('warehouse_receipt_lines');

    frappe.call({
        method: 'cargo_management.warehouse_management.utils.get_packages_by_agent_and_transportation',
        type: 'GET',
        args: {
            agent: frm.doc.agent,
            transportation: frm.doc.transportation
        },
        freeze: true,
        freeze_message: __('Adding Packages...'),
    }).then(r => {
        r.message.packages.forEach(package_doc => {
            frm.add_child('warehouse_receipt_lines', {
                'parcel': package_doc.name,
                'parcel_transportation': package_doc.transportation,  // إضافة الحقل transportation
                'parcel_customer': package_doc.shipper_name,
				'parcel_customer_name':package_doc.receiver_name,
				'type': package_doc.piece_type,  // إضافة الحقل piece_type
				// 'warehouse_est_weight':package_doc.total_actual_weight,
				// 'volumetric_weight': package_doc.total_volumetric_weight,
                'length': package_doc.total_net_length,
                'width': package_doc.total_net_width,
                'height': package_doc.total_net_height,
				'shipping_amount':package_doc.shipping_amount,
            });
        });

        // تحديث الجدول بعد إضافة البيانات
        frm.refresh_field('warehouse_receipt_lines');
    });
}

function calculate_total_amount_and_update_paid(frm) {
    frappe.call({
        method: 'calculate_total_amount',
        doc: frm.doc,
        callback: function(r) {
            if (r.message) {
                frm.set_value('total_shipment_amount', r.message);
                frm.refresh_field('total_shipment_amount'); // لتحديث الحقل في النموذج
            } else {
                console.log("Error calculating total amount.");
            }
        }
    });
}