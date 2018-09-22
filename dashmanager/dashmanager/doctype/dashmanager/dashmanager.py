# -*- coding: utf-8 -*-
# Copyright (c) 2018, AgriTheory and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.jinja import validate_template  # probably don't need this method, but likely other jinja utilities
import json

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
		# component type + dimensions (need templates for list, table, chart, status)

	def build_dashboard_components(self):
		print("Printing Components")
		components = []
		index = 0
		for component in self.components:
			components.append({
				"title": component.component_title,
				"type": component.component_type,
				"data": self.getDataForComponent(component.component_type, component, self.ref_doctype, self.ref_docfield),
				"template":self.getTemplateForComponent(component.component_type, component, self.ref_doctype, self.ref_docfield),
				"domid":self.ref_docfield+"_"+str(index)
			})
			index+=1
		return components
	
	def getTemplateForComponent(self, type, component, ref_doctype, ref_docfield):
		if type=="Chart":
			return "barcharttemplate"
		if type=="Table":
			return "tabletemplate"

	def getDataForComponent(self, type,component, ref_doctype, ref_docfield):
		### todo: rendering of data based on type of component.
		if type=="Chart":
			return self.getChartData(component, ref_doctype, ref_docfield)
		
		if type=="Table":
			return self.getTableData(component, ref_doctype, ref_docfield)
	
	def getChartData(self, component, ref_doctype, ref_docfield):
		## here the data will come from SQL and not statically
		return {
			"data": {
				"labels": ["12am-3am", "3am-6am", "6am-9am", "9am-12pm","12pm-3pm", "3pm-6pm", "6pm-9pm", "9pm-12am"],
				"datasets": [
					{
						"name": "Some Data", "chartType": 'bar',
						"values": [25, 40, 30, 35, 8, 52, 17, -4]
					},
					{
						"name": "Another Set", "chartType": 'bar',
						"values": [25, 50, -10, 15, 18, 32, 27, 14]
					},
					{
						"name": "Yet Another", "chartType": 'line',
						"values": [15, 20, -3, -15, 58, 12, -17, 37]
					}],
				"yMarkers": [{ "label": "Marker", "value": 70,"options": { "labelPos": 'left' }}],
				"yRegions": [{ "label": "Region", "start": -10, "end": 50,"options": { "labelPos": 'right' }}]
			},
			"title": "My Awesome Chart",
			"type": 'axis-mixed', ##// or 'bar', 'line', 'pie', 'percentage'
			"height": 300,
			"colors": ['purple', '#ffa3ef', 'light-blue'],
		}
		

	
	
	
	def getTableData(self, component, ref_doctype, ref_docfield):
		## here the data will come from SQL and not statically
		return {
			"columns": ['Name', 'Position', 'Salary'],
			"data": [['Faris', 'Software Developer', '$1200'],['Manas', 'Software Engineer', '$1400']]
		}



@frappe.whitelist()
def get_dashboard(doctype, active_document):
	frappe.msgprint("dashmanager")
	dash = frappe.get_doc("Dashmanager", {"doctype": doctype})
	dash.active_document = active_document
	return dash.build_components()

@frappe.whitelist()
def get_dashboard_components(doctype):
	dashs = frappe.get_all("Dashmanager", filters={"ref_doctype": doctype})
	print ("Got Dashes:"+str(dashs))
	fields = []
	for d in dashs:
		dash = frappe.get_doc("Dashmanager",d)
		print("Got Dash:", str(dash))
		fields.append({
			"ref_docfield":dash.ref_docfield,
			"components":dash.build_dashboard_components()
		})
	## changing this to return the rendered template instead of just json data.
	##return fields

	## a test... response will go field wise.. 
	return frappe.render_template("dashmanager/templates/barcharttemplate.html", {
		"component":fields[0]["components"][0] ,
		"componentdatajson" : json.dumps(fields[0]["components"][0]["data"])
	})

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
