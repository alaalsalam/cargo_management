frappe.listview_settings['Parcel'] = {
	hide_name_filter: true,
	add_fields: ['carrier'],
	filters: [
		['status', 'not in', ['Finished', 'Cancelled', 'Never Arrived', 'Returned to Sender']] // aka 'Active Parcels'
	],


	onload(listview) {
		const {tracking_number: tracking_number_field, customer_name: customer_name_field} = listview.page.fields_dict;

		listview.page.sidebar.toggle(false);

		// Override: onchange() method set in frappe/list/base_list.js -> make_standard_filters()
		// tracking_number_field.df.onchange = customer_name_field.df.onchange = function () {
		// 	// Remove '%' added in frappe/list/base_list.js -> get_standard_filters() when the listview loads and update both UI and internal values
		// 	this.value = this.input.value = this.get_input_value().replaceAll('%', '').trim().toUpperCase(); // this.set_input() is not working

		// 	if (this.value !== this.last_value) {
		// 		listview.filter_area.refresh_list_view(); // refresh_list_view() if the value has changed
		// 	}
		// };

		/* Override to add 'or_filters'. FIXME: Will be better to have it on backend to solve: gets_args + get_count_str + get_stats
		 * frappe hook: 'permission_query_conditions' Wont work, It get called after we have build the frappe
		 * check this: override_whitelisted_methods. The problem is this method is HEAVILY used
		 * TODO: listview.get_count_str() => This call frappe.db.count() using 'filters' not 'or_filters'
		 * TODO: listview.list_sidebar.get_stats() => This call frappe.desk.reportview.get_sidebar_stats using 'filters' not 'or_filters' */
		listview.get_args = function () {
			let args = frappe.views.ListView.prototype.get_args.call(listview);  // Calling his super for the args

			const tracking_number_filter = args.filters.findIndex(f => f[1] === 'tracking_number');  // f -> ['Doctype', 'field', 'sql_search_term', 'value']

			if (tracking_number_filter >= 0) {  // We have 'tracking_name' filter being filtered. -> tracking_number_filter will contain index if found
				args.filters.splice(tracking_number_filter, 1);  // Removing 'name' filter from 'filters'. It's a 'standard_filter'

				// const search_term = cargo_management.find_carrier_by_tracking_number(tracking_number_field.get_input_value()).search_term;

				// TODO: WORK -> We will not use the main field from now on
				// args.or_filters = ['name', 'tracking_number'].map(field => [
				// 	args.doctype, field, 'like', '%' + search_term + '%'
				// ]); // Mapping each field to 'or_filters' for the necessary fields to search
				// args.or_filters.push(['Parcel Content', 'tracking_number', 'like', '%' + search_term + '%'])  // This acts as a consolidated tracking number
			}

			return args;
		};
	},

	// Unused: light-blue. // TODO: Migrate to Document States? Maybe when frappe core starts using it.
	get_indicator: (doc) => [__(doc.status), {
		'Awaiting Receipt': 'blue',
		'Awaiting Confirmation': 'orange',
		'In Extraordinary Confirmation': 'pink',
		'Awaiting Departure': 'yellow',
		'In Transit': 'purple',
		'In Customs': 'gray',
		'Sorting': 'green',
		'To Bill': 'green',
		'Unpaid': 'red',
		'For Delivery or Pickup': 'cyan',
		'Finished': 'darkgrey',
		'Cancelled': 'red',
		'Never Arrived': 'red',
		'Returned to Sender': 'red',
	}[doc.status], 'status,=,' + doc.status],

	button: {
		show: () => true,
		get_label: () => __('Preview'),
		get_description: () => '',
		action(doc) {
			this.parcel_preview_dialog(doc)
		// 	let fields = [...this.build_carrier_urls(__('Tracking Number'), doc.tracking_number, doc.carrier)];

		// 	if (doc.name !== doc.tracking_number) {
		// 		fields.unshift(...this.build_carrier_urls(__('Name'), doc.name));
		// 	}

		// 	if (doc.consolidated_tracking_numbers) {
		// 		doc.consolidated_tracking_numbers.split('\n').forEach((tracking_number, i) => {
		// 			fields.push(...this.build_carrier_urls(__('Consolidated #{0}', [i + 1]), tracking_number));
		// 		});
		// 	}

		// 	new frappe.ui.Dialog({animate: false, size: 'small', indicator: 'green', title: this.get_label, fields: fields}).show();
		},
		parcel_preview_dialog(doc) {
			const preview_dialog = new frappe.ui.Dialog({
				title: 'General Overview', size: 'extra-large',
				fields: [
					{ fieldtype: 'HTML', fieldname: 'preview' },
				]
			});
		
			preview_dialog.show();
		
			const content = doc.content || [];
			const contentHtml = content.map(c => `
				<li class="list-group-item">
					Descripcion: <strong>${c.description}</strong> | Tracking: <strong>${c.tracking_number}</strong>
				</li>`).join('');
		
			preview_dialog.fields_dict.preview.$wrapper.html(`
		<div class="container">
			<h3 class="text-center">${doc.tracking_number} -${doc.shipper_name}</h3>

			<div class="row">
				<div class="col-6">
					<div class="card">
						<div class="card-header">General Information</div>
						<ul class="list-group list-group-flush">
							<li class="list-group-item">Shipper Name: <strong>${doc.shipper_name}</strong></li>
							<li class="list-group-item">Receiver Name: <strong>${doc.receiver_name}</strong></li>
							<li class="list-group-item">Destination : <strong>${doc.destination}</strong></li>
						</ul>
					</div>
				</div>
				<div class="col-6">
					<div class="card">
						<div class="card-header">Descripcion</div>
						<ul class="list-group list-group-flush">
									${contentHtml}
								</ul>
					</div>
				</div>
			</div>
			<div class="flex-row justify-content-between align-items-start border rounded p-3 my-3">
						<div class="card">
						<div class="card-header">Note</div>
						<ul class="list-group list-group-flush">
							<li class="list-group-item">Additional Notes: <strong>${doc.notes}</strong></li>
						</ul>
					</div>
				</div>
			</div>
			<div class="d-flex flex-row justify-content-between align-items-start border rounded p-3 my-3">
				<div>
					<div class="mb-2"><span class="badge badge-primary">Order Date</span> <strong>${doc.order_date}</strong></div>
				</div>
				<div class="d-flex flex-column">
					<div class="mb-2"><span class="badge badge-secondary">Estimated Delivery Date (Earliest) 1</span> <strong>${doc.est_delivery_1}</strong></div>
					<div><span class="badge badge-secondary">Estimated Delivery Date (Latest) 2</span> <strong>${doc.est_delivery_2}</strong></div>
				</div>
				<div>
					<div><span class="badge badge-success">Estimated Departure Date</span> <strong>${doc.est_departure}</strong></div>
				</div>
				<div>
					<div><span class="badge badge-success">Carrier estimated delivery date</span> <strong>${doc.est_departure}</strong></div>
				</div>
			</div>

		</div>`);
		}
		

	},

	// formatters: {
	// 	transportation: (value) => cargo_management.transportation_formatter(value),
	// 	name: (value, df, doc) => (value !== doc.tracking_number) ? `<b>${value}</b>` : ''
	// }
};
