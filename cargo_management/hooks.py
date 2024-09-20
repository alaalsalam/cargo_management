app_name = "cargo_management"
app_title = "Cargo Management"
app_publisher = "Agile Shift"
app_description = "ERPNext Cargo Management for Freight Forwarders"
app_email = "contacto@gruporeal.org"
app_license = "agpl-3.0"
# required_apps = []

# Includes in <head>
# ------------------

# include JS, CSS files in header of desk.html
app_include_css = "cargo_management.bundle.css"
app_include_js = "cargo_management.bundle.js"

# app_include_css = "/assets/cargo_management/dist/css/cargo_management.bundle.6RMC5W2E.css"
# app_include_css = "/assets/cargo_management/dist/css-rtl/cargo_management.bundle.EMV7DFB6.css"
# app_include_css = "/assets/cargo_management/scss/cargo_management.bundle.scss"
# app_include_css = "/assets/cargo_management/scss/colors.scss"
# app_include_js = "/assets/cargo_management/js/overrides.scss"

# include JS, CSS files in header of web template
# web_include_css = "/assets/cargo_management/css/parcel_management.css"
# web_include_js = "/assets/cargo_management/js/parcel_management.js"

# include custom SCSS in every website theme (without file extension ".scss")
# website_theme_scss = "v15/public/scss/website"

# include JS, CSS files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/list_viwe.js"}
# app_include_js = "public/js/list_viwe.js"
import frappe
import frappe

@frappe.whitelist()
def get_doctypes():
    doctypes = frappe.get_all('DocType', filters={'issingle': 0, 'istable': 0, 'custom': 0}, fields=['name'])
    return [doctype['name'] for doctype in doctypes]

@frappe.whitelist()
def get_non_table_doctypes():
    doctypes = frappe.get_all('DocType', filters={'issingle': 0,'istable': 0,'custom': 0}, fields=['name'])
    docs_dics = {}
    for doctype in doctypes:
        docs_dics[doctype.name] = "public/js/list_view.js" 
    # return [doctype['name'] for doctype in doctypes]
    return docs_dics



doctype_list_js = get_non_table_doctypes()
# doctype_list_js = {"*" : "public/js/list_view.js"}

# Include js in doctype views: override/extend Standard Form Scripts.
doctype_js = {
	"Quotation": "public/js/quotation.js"  # TODO: WORKING HERE
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#    "Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "cargo_management.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#   "methods": "v15.utils.jinja_methods",
#   "filters": "v15.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "cargo_management.install.before_install"
# after_install = "cargo_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "cargo_management.uninstall.before_uninstall"
# after_uninstall = "cargo_management.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "v15.utils.before_app_install"
# after_app_install = "v15.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "v15.utils.before_app_uninstall"
# after_app_uninstall = "v15.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "cargo_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Parcel": "cargo_management.parcel_management.doctype.parcel.events.get_permission_query_conditions",
# }

# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#   "ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# standard_queries = {
# 	"Parcel": "cargo_management.parcel_management.doctype.parcel.events.get_parcel_query",
# }

doc_events = {
	"Sales Invoice": {  # TODO: WORKING
		"on_submit": "cargo_management.parcel_selling.utils.sales_invoice_on_submit",
		"on_change": "cargo_management.parcel_selling.utils.sales_invoice_on_update_after_submit"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#   "all": [
#      "v15.tasks.all"
#   ],
#   "daily": [
#   "v15.tasks.daily"
#   ],
#   "hourly": [
#      "v15.tasks.hourly"
#   ],
#   "weekly": [
#      "v15.tasks.weekly"
#   ],
#   "monthly": [
#      "v15.tasks.monthly"
#   ],
# }

# Testing
# -------

# before_tests = "cargo_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "cargo_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "cargo_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["v15.utils.before_request"]
# after_request = ["v15.utils.after_request"]

# Job Events
# ----------
# before_job = ["v15.utils.before_job"]
# after_job = ["v15.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#   {
#      "doctype": "{doctype_1}",
#      "filter_by": "{filter_by}",
#      "redact_fields": ["{field_1}", "{field_2}"],
#      "partial": 1,
#   },
#   {
#      "doctype": "{doctype_2}",
#      "filter_by": "{filter_by}",
#      "partial": 1,
#   },
#   {
#      "doctype": "{doctype_3}",
#      "strict": False,
#   },
#   {
#      "doctype": "{doctype_4}"
#   }
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#   "v15.auth.validate"
# ]
doc_events = {
    "Parcel Content": {
        "on_update": "cargo_management.parcel_management.doctype.parcel.parcel.calculate_shipping_amountt",
    }
}

# scheduler_events = {
#     "daily": [
#         "your_app_path.update_cargo_shipment_status"
#     ]
# }


global_search_doctypes = {
	"Default": [
		{"doctype": "Parcel"},
		{"doctype": "Warehouse Receipt"},
		{"doctype": "Cargo Shipment"},
		{"doctype": "Cargo Shipment Receipt"},
	]
}

fixtures = [
	'Issue Type',
	{'dt': 'Workspace', 'filters': {'name': 'Support'}}
]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# extend_bootinfo = "cargo_management.utils.extend_bootinfo"