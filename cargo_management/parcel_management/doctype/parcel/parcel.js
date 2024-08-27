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
	setup(frm) {
	},

	onload(frm) {
		frm.page.sidebar.toggle(false);
		// FIXME: Observe if the indicator changes. This is useful for the 'Not Saved' status aka is_dirty(). We cannot read that from the events available
		// const observer = new MutationObserver(() => {
		// 	frm.layout.show_message('');     // Clear Message because it's possible that data changes!
		// 	frm.page.clear_custom_actions(); // Clear Custom buttons
		// 	frm.page.indicator.next().remove(); // Remove the extra indicator if the indicator changes
		// });

		// observer.observe(frm.page.indicator.get(0), {childList: true}); // Observe the 'indicator' for changes

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
		frm.set_value('total', frm.get_sum('content', 'amount') + frm.doc.shipping_amount);
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
	parcel_price_rule(frm) {
		if(frm.doc.parcel_price_rule) {
			return frm.call({
				doc: frm.doc,
				method: "apply_parcel_price_rule",
				callback: function(r) {
					calculate_content_amounts_and_total();
				}
			}).fail(() => frm.set_value('parcel_price_rule', ''));
		}
	}
	
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
