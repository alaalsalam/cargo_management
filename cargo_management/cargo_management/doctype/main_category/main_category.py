# Copyright (c) 2024, Agile Shift and contributors
# For license information, please see license.txt

# import frappe
from frappe.utils.nestedset import NestedSet


class MainCategory(NestedSet):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from cargo_management.cargo_management.doctype.sub_category.sub_category import SubCategory
		from frappe.types import DF

		is_group: DF.Check
		lft: DF.Int
		name1: DF.Data
		old_parent: DF.Link | None
		parent_main_category: DF.Link | None
		rgt: DF.Int
		table_dgfl: DF.Table[SubCategory]
	# end: auto-generated types
	pass
