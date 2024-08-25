frappe.ui.form.on('Warehouse Receipt', {

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
	},

	setup: function (frm) {
		frm.page.sidebar.toggle(false); // Hide Sidebar

		if (frm.is_new())
			frm.events.transportation_multi_check(frm);
	},

	onload_post_render: function (frm) {},

	before_save: function (frm) {},

	after_save: function (frm) {},

	tracking_number: function (frm) {
		frm.doc.tracking_number = frm.doc.tracking_number.trim().toUpperCase();  // Sanitize field

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
        if (!frm.doc.agent) {
            return;
        }

        fetch_packages_by_agent_and_transportation(frm);
    },
    
    transportation: function(frm) {
        if (!frm.doc.agent) {
            return;
        }

        fetch_packages_by_agent_and_transportation(frm);
    },
	
	
	// agent: function (frm) {
	// 	if (!frm.doc.agent) {
	// 		return;
	// 	}

	// 	// We clear the table each time to avoid duplication
	// 	frm.clear_table('warehouse_receipt_lines');

	// 	frappe.call({
	// 		method: 'cargo_management.shipment_management.utils.get_parcel_in_parcel',
	// 		type: 'GET',
	// 		args: {agent: frm.doc.agent},
	// 		freeze: true,
	// 		freeze_message: __('Adding Packages...'),
	// 	}).then(r => {

	// 		r.message.packages.forEach(parcel_doc => {
	// 			frm.add_child('warehouse_receipt_lines', {
	// 				'parcel': parcel_doc.name,
	// 				'parcel_transportation': parcel_doc.parcel_transportation,
	// 				// 'item_code': package_doc.item_code, TODO: This is not working, because the package can have more than one item code
	// 				'customer': parcel_doc.customer,
	// 				'customer_name': parcel_doc.customer_name,
	// 				'type': parcel_doc.type,
	// 			});
	// 		});

	// 		// Refresh the modified tables inside the callback after execution is done
	// 		frm.refresh_field('warehouse_receipt_lines');
	// 	});
	// },

	show_alerts: function(frm) {
		// TODO: Make this come from API?
		frm.dashboard.clear_headline();

		if (frm.doc.customer_description) {
			frm.layout.show_message('<b>No es necesario abrir el paquete. <br> Cliente Pre-Alerto el contenido.</b>', '');
			frm.layout.message.removeClass().addClass('form-message ' + 'green');  // FIXME: Core overrides color
		}
	},
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
				'warehouse_est_weight':package_doc.total_actual_weight,
				'volumetric_weight': package_doc.total_volumetric_weight,
                'length': package_doc.total_net_length,
                'width': package_doc.total_net_width,
                'height': package_doc.total_net_height,
            });
        });

        // تحديث الجدول بعد إضافة البيانات
        frm.refresh_field('warehouse_receipt_lines');
    });
}
frappe.ui.form.on('Warehouse Receipt Line', {}); // FIXME 134
