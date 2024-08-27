from frappe import _


def get_data():
	return {
		"fieldname": "agent",
		"non_standard_fieldnames": {
			"Payment Entry": "party",
			"Quotation": "party_name",
			"Opportunity": "party_name",
			"Bank Account": "party",
			"Subscription": "party",
            "Issue":"custom_agent",
		},
		"dynamic_links": {"party_name": ["Agent", "quotation_to"]},
		"transactions": [
			{"label": _("Pre Sales"), "items": ["Opportunity", "Quotation"]},
			{"label": _("Orders"), "items": ["Sales Order", "Delivery Note", "Sales Invoice"]},
			{"label": _("Payments"), "items": ["Payment Entry", "Bank Account"]},
			{
				"label": _("Support"),
				"items": ["Issue"],
			},
			# {"label": _("Projects"), "items": ["Project"]},
			# {"label": _("Pricing"), "items": ["Pricing Rule"]},
			{"label": _("Subscriptions"), "items": ["Subscription"]},
		],
	}
