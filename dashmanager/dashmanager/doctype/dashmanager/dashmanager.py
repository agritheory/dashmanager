# -*- coding: utf-8 -*-
# Copyright (c) 2018, AgriTheory and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.jinja import validate_template  # probably don't need this method, but likely other jinja utilities
import json
from  DashComponentsWrappers import * 


class Dashmanager(Document):
	# validation methods
	def validate(self):
		self.make_custom_script()
		self.validate_duplicates()
	
	def validate_duplicates(self):
		existing_docs = frappe.get_all("Dashmanager", filters={"ref_doctype":self.ref_doctype, "ref_docfield":self.ref_docfield})
		if len (existing_docs) > 0:
			if existing_docs[0].name != self.name: 
				frappe.throw("Cannot have two Dashmanagers for same DocType and Custom Field")

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
		rendered_htmls = []
		boostrap_setting_dict = get_boostrap_settings()
		
		for component in self.components:
			component_obj = {
				"title": component.component_title,
				"type": component.component_type,
				"data": self.getDataForComponent(component.component_type, component, self.ref_doctype, self.ref_docfield),
				"domid":self.ref_docfield+"_"+str(index)
			} ## some fields may not be required. Will remove in future
			print("Data", component_obj["data"])
			template_to_render = self.getTemplateForComponent(component.component_type, component, self.ref_doctype, self.ref_docfield)
			rendered_htmls.append(
				frappe.render_template(template_to_render, {
				"component":component_obj ,
				"componentdatajson" : json.dumps(component_obj["data"]),
				"col_class":boostrap_setting_dict[component.component_size]
				})
			)
			
			# components.append({
			# 	"title": component.component_title,
			# 	"type": component.component_type,
			# 	"data": self.getDataForComponent(component.component_type, component, self.ref_doctype, self.ref_docfield),
			# 	"template":self.getTemplateForComponent(component.component_type, component, self.ref_doctype, self.ref_docfield),
			# 	"domid":self.ref_docfield+"_"+str(index)
			# })
			index+=1

		return "".join(rendered_htmls)#components
	
	def getTemplateForComponent(self, type, component, ref_doctype, ref_docfield):
		## TODO: to put a dict mapping instead of the lousy if...
		if type=="Chart":
			return "dashmanager/templates/barcharttemplate.html"
		if type=="Table":
			return "dashmanager/templates/simpletabletemplate.html"
		if type=="List":
			return "dashmanager/templates/listtemplate.html"
		if type=="Value":
			return "dashmanager/templates/valuestemplate.html"

	def getDataForComponent(self, type,component, ref_doctype, ref_docfield):
		### todo: rendering of data based on type of component.
		if type=="Chart":
			return self.getChartData(component, ref_doctype, ref_docfield)
		
		if type=="Table":
			return self.getTableData(component, ref_doctype, ref_docfield)
		
		if type=="List":
			return self.getListData(component, ref_doctype, ref_docfield)
		
		if type=="Value":
			return self.getValuesData(component, ref_doctype, ref_docfield)
	
	def getChartData(self, component, ref_doctype, ref_docfield):
		## here the data will come from SQL and not statically


		settings = {
			"title": component.component_title,
			"type": 'axis-mixed', ##// or 'bar', 'line', 'pie', 'percentage'
			"height": 300,
			"colors": ['purple', '#ffa3ef', 'light-blue']
		}
		
		chartModel = ChartModel(settings)
		chartModel.setLabels(ChartLabel(["12am-3am", "3am-6am", "6am-9am", "9am-12pm","12pm-3pm", "3pm-6pm", "6pm-9pm", "9pm-12am"]))
		chartModel.addDataSets(ChartDataSet("Some Data 1", [25, 40, 30, 35, 8, 52, 17, -4],"bar"))
		chartModel.addDataSets(ChartDataSet("Some Data 1", [25, 50, -10, 15, 18, 32, 27, 14],"bar"))
		chartModel.addDataSets(ChartDataSet("Some Data 1", [15, 20, -3, -15, 58, 12, -17, 37],"bar"))

		return chartModel.generateChartModelObject()
		
		# return {
		# 	"data": {
		# 		"labels": ["12am-3am", "3am-6am", "6am-9am", "9am-12pm","12pm-3pm", "3pm-6pm", "6pm-9pm", "9pm-12am"],
		# 		"datasets": [
		# 			{
		# 				"name": "Some Data", "chartType": 'bar',
		# 				"values": [25, 40, 30, 35, 8, 52, 17, -4]
		# 			},
		# 			{
		# 				"name": "Another Set", "chartType": 'bar',
		# 				"values": [25, 50, -10, 15, 18, 32, 27, 14]
		# 			},
		# 			{
		# 				"name": "Yet Another", "chartType": 'line',
		# 				"values": [15, 20, -3, -15, 58, 12, -17, 37]
		# 			}],
		# 		"yMarkers": [{ "label": "Marker", "value": 70,"options": { "labelPos": 'left' }}],
		# 		"yRegions": [{ "label": "Region", "start": -10, "end": 50,"options": { "labelPos": 'right' }}]
		# 	},
		# 	"title": component.component_title,
		# 	"type": 'axis-mixed', ##// or 'bar', 'line', 'pie', 'percentage'
		# 	"height": 300,
		# 	"colors": ['purple', '#ffa3ef', 'light-blue'],
		# }
		

	
	
	
	def getTableData(self, component, ref_doctype, ref_docfield):
		## here the data will come from SQL and not statically

		table = Table(["One", "Two", "Three"], [
				["Data 1","Data 2","Data 3"],
				["Data 12","Data 2","Data 3"]
			])

		return table.generateTableModelObject()
		
		# {
		# 	"columns": ["One", "Two", "Three"],
		# 	"rows" : [
		# 		["Data 1","Data 2","Data 3"],
		# 		["Data 1","Data 2","Data 3"]
		# 	],"settings":{
		# 		"rowno":True
		# 	}
		# }
		# return {
		# 	"columns": json.dumps([{
		# 		"name":"Name",
		# 		"field":"name",
		# 		"id":"name"
		# 	},{
		# 		"name":"Age",
		# 		"field":"age",
		# 		"id":"age"
		# 	},{
		# 		"name":"Number",
		# 		"field":"number",
		# 		"id":"number"
		# 	},{
		# 		"name":"Description",
		# 		"field":"description",
		# 		"id":"description",
		# 		"width":300
		# 	}
		# 	]),
		# 	"data": json.dumps([{
		# 		"name":"John",
		# 		"age":12,
		# 		"number":999923993993,
		# 		"description":"This is a dummy text.This is a dummy text."
		# 	},{
		# 		"name":"Doe",
		# 		"age":14,
		# 		"number":999923993993,
		# 		"description":"This is a dummy text.This is a dummy text."
		# 	},{
		# 		"name":"Doe",
		# 		"age":14,
		# 		"number":999923993993,
		# 		"description":"This is a dummy text.This is a dummy text."
		# 	},{
		# 		"name":"Doe",
		# 		"age":14,
		# 		"number":999923993993,
		# 		"description":"This is a dummy text.This is a dummy text."
		# 	}])
		# }
	
	def getListData(self, component, ref_doctype, ref_docfield):
		settings = {
			"type":"ordered",
			"bullets":True,
			"hasvalues":True
		}

		list = List([ListItem("One","Value 1"),ListItem("Two","Value 2"),ListItem("Three","Value 3")])
		list.setSettings(settings)
		# list.
		
		
		return list.generateListModelObject()
	
	def getStatusData(self, component, ref_doctype, ref_docfield):
		pass

	def getValuesData(self, component, ref_doctype, ref_docfield):
		return {
			"caption": "Total Sales",
			"value":"$100000"
		}



@frappe.whitelist()
def get_dashboard(doctype, active_document):
	frappe.msgprint("dashmanager")
	dash = frappe.get_doc("Dashmanager", {"doctype": doctype})
	dash.active_document = active_document
	return dash.build_components()

@frappe.whitelist()
def get_dashboard_components(doctype, field):
	dashs = frappe.get_all("Dashmanager", filters={"ref_doctype": doctype,"ref_docfield":doctype+"-"+field})
	## for a given dashboard and fields, there will be a single dashmanager record.
	print("Dashs:",dashs)
	dash = frappe.get_doc("Dashmanager", dashs[0])
	return dash.build_dashboard_components()
	## changing this to return the rendered template instead of just json data.
	## return fields

	## a test... response will go field wise.. 
	##return ""
	# # frappe.render_template("dashmanager/templates/barcharttemplate.html", {
	# 	"component":fields[0]["components"][0] ,
	# 	"componentdatajson" : json.dumps(fields[0]["components"][0]["data"])
	# })

@frappe.whitelist()
def get_dashmanager_docs():
	#### this should return all the documents for which the dashmanager has a registered component.
	
	## getting all doctypes from all dashmanagers
	ref_docs = get_registered_docs_for_dashmanager()
	
	return {
		"ref_docs" : json.dumps(ref_docs)
	}

def get_registered_docs_for_dashmanager():
	dash_docs = frappe.get_all("Dashmanager", filters={},fields=["ref_doctype"])	
	ref_docs = []
	for dash_doc in dash_docs:
		if not dash_doc.ref_doctype in ref_docs:
			ref_docs.append(str(dash_doc.ref_doctype))
	return ref_docs

@frappe.whitelist()
def get_dashmanager_field_components(doctype):
	## get list of fields and components for given doc type
	fields_list, fields_component_list = get_fields_component_list(doctype)
	return {
		"fields" : json.dumps(fields_list),
		"fields_components" : json.dumps(fields_component_list)
	}

def get_fields_component_list(doctype):
	dashs = frappe.get_all("Dashmanager", filters={"ref_doctype": doctype})
	fields_list = []
	fields_component_list = {}
	for dash in dashs:
		dash_doc = frappe.get_doc("Dashmanager", dash)
		field = str(dash_doc.ref_docfield).split("-")[1]
		fields_list.append(field)
		filtered_components = []
		for c in dash_doc.components:
			component = {
				"component_title":c.component_title,
				"component_type":c.component_type
			}
			filtered_components.append(component)
		
		fields_component_list[field] =  filtered_components
	
	return fields_list, fields_component_list

@frappe.whitelist()
def get_dashmanager_components_settings():
	boostrap_setting_dict = get_boostrap_settings()
	icon_settings_dict = get_icon_settings()

	response = {
		"boostrap_settings" : boostrap_setting_dict,
		"icon_settings":icon_settings_dict
	}

	return json.dumps(response)

def get_boostrap_settings():
	boostrap_setting_dict = {}
	boostrap_settings = frappe.get_all("Dashmanager Component Setting", filters={"setting_type":"Bootstrap Class"}, fields=["setting_key", "setting_value"])
	for bsetting in boostrap_settings:
		boostrap_setting_dict[bsetting.setting_key] = bsetting.setting_value
	return boostrap_setting_dict

def get_icon_settings():
	icon_settings_dict = {}
	icon_settings = frappe.get_all("Dashmanager Component Setting", filters={"setting_type":"Icon"}, fields=["setting_key", "setting_value"])
	for isetting in icon_settings:
		icon_settings_dict[isetting.setting_key] = isetting.setting_value
	return icon_settings_dict


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
