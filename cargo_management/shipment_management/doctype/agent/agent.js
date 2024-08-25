// Copyright (c) 2024, Agile Shift and contributors
// For license information, please see license.txt

frappe.ui.form.on("Agent", {
	setup(frm) {
		frm.set_query("user", "portal_users", function () {
			return {
				filters: {
					ignore_user_type: true,
				},
			};
		});
	},
});
