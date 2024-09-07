// Copyright (c) 2024, Agile Shift and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shipment Settings", {
	setup(frm) {
        frm.set_query("account", "accounts", function (doc, cdt, cdn) {
			return {
				filters: {
					root_type: "Liability",
					account_type: "Payable",
					company: locals[cdt][cdn].company,
					is_group: 0,
				},
			};
		});
		frm.set_query("advance_account", "accounts", function (doc, cdt, cdn) {
			return {
				filters: {
					root_type: "Asset",
					account_type: "Payable",
					company: locals[cdt][cdn].company,
					is_group: 0,
				},
			};
		});
	},
});
