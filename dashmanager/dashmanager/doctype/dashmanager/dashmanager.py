# -*- coding: utf-8 -*-
# Copyright (c) 2018, AgriTheory and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.jinja import validate_template  # probably don't need this method, but likely other jinja utilities


class Dashmanager(Document):
	# validation methods
	def validate(self):
		self.make_custom_script()

	def sql_builder(self):
		pass
		#

	def make_custom_script(self):
		script_name = frappe.db.sql("""
		select name from `tabCustom Script`
		where name = %(script_name)s
		""", {"script_name": self.ref_doctype + "-Client"}, as_dict=True)
		if not script_name:
			new_script = frappe.new_doc("Custom Script")
			new_script.dt = self.ref_doctype
			new_script.script = "frappe.ui.form.on(\"" + self.ref_doctype + script
		else:
			new_script = frappe.get_doc("Custom Script", script_name[0]["name"])
			if "dashmanager" in new_script.script:
				return
			else:
				new_script.script = new_script.script + "\n \n frappe.ui.form.on(\"" + self.ref_doctype + script
				new_script.save()

	# rendering methods

	def build_components(self):
		dash = []
		pass
		# for component in components:
			# self.run_query(component)
			# template = self.load_template(component)
			# dash.append(frappe.scrub(component.title): template)
		# return dash

	def run_query(self):
		pass
		# if within cached datetime period, return cache
		# else: self.sql_builder

	def load_template(self, component):
		pass
		# path to jinja "list" template
		# component type + dimensions (need templates for list, table, )


@frappe.whitelist()
def get_dashboard(doctype, active_document):
	frappe.msgprint("dashmanager")
	dash = frappe.get_doc("Dashmanager", {"doctype": doctype})
	dash.active_document = active_document
	return dash.build_components()


script = """\", {
	refresh: frm => {
		frappe.call({
			method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashboard",
			args: {"doctype": frm.doc.doctype, "active_document": frm.doc.name}
		}).done((r) => {
			let populate = document.getElementById(r.message.docfield);
			populate.innerHTML = r.message.dashmanager;
		}).fail((r) => {
			console.log(r);
		});
	}
});
"""
