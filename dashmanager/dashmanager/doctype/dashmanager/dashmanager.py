# -*- coding: utf-8 -*-
# Copyright (c) 2018, AgriTheory and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from .... import ChartModel, ChartDataSet, ChartLabel, Table, List,\
	ListItem, SummaryValue, StatusField
import datetime
import time


class Dashmanager(Document):
	syncTimes = {
		"Hourly": 20,  # 60*60,
		"Daily": 30,  # 24*60*60,
		"Weekly": 60  # 7*24*60*60
	}
	# validation methods

	def validate(self):
		# self.make_custom_script()
		self.validate_duplicates()
		self.validate_components()
		if self.dashmanager_type != "DocType":
			self.set_page()

	def validate_duplicates(self):
		existing_docs = frappe.get_all("Dashmanager",
			filters={"ref_doctype": self.ref_doctype, "ref_docfield": self.ref_docfield})
		if len(existing_docs) > 0:
			if existing_docs[0].name != self.name:
				frappe.throw("Cannot have two Dashmanagers for same DocType and Custom Field")

	def set_page(self):
		self.ref_docfield = "dashmanager-content"

	def validate_components(self):
		for component in self.components:
			if component.data_source == "SQL":
				# check the queries of all the Components
				if component.component_contents:
					self.validateQuery(component.component_contents, component)
			if component.data_source == "Hook":
				self.check_for_blank_hooks(component)

	def check_for_blank_hooks(self, component):
		if component.data_source == "Hook":
			if not component.hook_name or component.hook_name == "":
				frappe.throw("Hook name cannot be blank for component: " +
					str(component.component_title))

	# rendering methods
	def build_dashboard_components(self, doc):
		rendered_htmls = []
		boostrap_setting_dict = get_boostrap_settings()

		for index, component in enumerate(self.components):
			dirty = True
			nowDt = datetime.datetime.now()
			nowTs = time.mktime(nowDt.timetuple())

			if component.cache_this_components_query:
				timestamp_delta = self.syncTimes[component.cache_this_components_query]
				print("Delta", timestamp_delta)
				if self.components[index].last_cached:
					thenTs = time.mktime(self.components[index].last_cached.timetuple())
					print("Diff:", str(nowTs - thenTs))
					if nowTs > thenTs and (nowTs - thenTs) < timestamp_delta:
						dirty = False
			rendered_html = ""

			if dirty:
				print ("DIRTY")
				component_obj = {
					"title": component.component_title,
					"type": component.component_type,
					"data": self.getDataForComponent(component.component_type,
						component, self.ref_doctype, self.ref_docfield, doc),
					"domid": self.ref_docfield + "_" + str(index)
				}  # some fields may not be required. Will remove in future

				# print("Data", component_obj["data"])
				template_to_render = self.getTemplateForComponent(component.component_type,
					component, self.ref_doctype, self.ref_docfield)

				rendered_html = frappe.render_template(template_to_render, {
					"component": component_obj,
					"componentdatajson": json.dumps(component_obj["data"]),
					"col_class": boostrap_setting_dict[component.component_size]})

				self.components[index].cached_data = rendered_html

			else:
				print("NOTDIRTY")
				rendered_html = component.cached_data

			rendered_htmls.append(rendered_html)
			self.components[index].last_cached = nowDt
		# save the last cache time of each components....
		self.save()
		return "".join(rendered_htmls)  # components

	def getTemplateForComponent(self, type, component, ref_doctype, ref_docfield):
		if type == "Chart":
			return "dashmanager/templates/barcharttemplate.html"
		if type == "Table":
			return "dashmanager/templates/simpletabletemplate.html"
		if type == "List":
			return "dashmanager/templates/listtemplate.html"
		if type == "Value":
			return "dashmanager/templates/valuestemplate.html"
		if type == "Status":
			return "dashmanager/templates/statusfieldtemplate.html"

	def getDataForComponent(self, type, component, ref_doctype, ref_docfield, doc):
		if type == "Chart":
			return self.getChartData(component, ref_doctype, ref_docfield, doc)
		elif type == "Table":
			return self.getTableData(component, ref_doctype, ref_docfield, doc)
		elif type == "List":
			return self.getListData(component, ref_doctype, ref_docfield, doc)
		elif type == "Value":
			return self.getValuesData(component, ref_doctype, ref_docfield, doc)
		elif type == "Status":
			return self.getStatusData(component, ref_doctype, ref_docfield, doc)

	def getDataFromDataSource(self, component, ref_doctype, ref_docfield, doc, datasource, hook):
		if datasource == "Hook":
			return self.getTheHook(hook, ref_doctype, ref_docfield, doc)
		elif datasource == "SQL":
			# check if there is a seperator
			query = component.component_contents
			if self.checkIfMultipleQuery(query):
				# get all queries...
				if not component.component_type == "Chart":
					raise Exception("Multiple Queries supported only in ")
				queries = str(query).split(":::")
				data = []
				for q in queries:
					newrow = []
					for row in self.getQueryResult(q, component):
						newrow.append(row[0])
					data.append(newrow)
				return self.convertSqlToWrapperObjects(component, data)
			else:
				if component.component_type == "Chart":
					data = []
					newrow = []
					for row in self.getQueryResult(component.component_contents, component):
						newrow.append(row[0])
					data.append(newrow)
					return self.convertSqlToWrapperObjects(component, data)
				else:
					return self.convertSqlToWrapperObjects(component,
						self.getQueryResult(component.component_contents, component))

	def convertSqlToWrapperObjects(self, component, data):
		if component.component_type == "Chart":
			chartModel = ChartModel()
			chartModel.setLabels(ChartLabel(str(component.chart_labels).splitlines(False)))
			dset_names = str(component.dataset_names).splitlines(False)
			hasDataSetNames = (len(dset_names) == len(data))
			for index, row in enumerate(data):
				# print ("Got Row:", row)
				if hasDataSetNames:
					chartModel.addDataSets(ChartDataSet(row, dset_names[index]))
				else:
					chartModel.addDataSets(ChartDataSet(row))
			return chartModel

		if component.component_type == "Table":
			table = Table(str(component.table_columns).splitlines(False), data)
			if component.knowmoretext:
				table.setSettings({"knowmoretext": component.knowmoretext})
			return table

		if component.component_type == "List":
			single = False
			if len(data[0]) == 2:
				list_arr = [ListItem(row[0], row[1]) for row in data]
			elif len(data[0]) == 1:
				list_arr = [ListItem(row[0], None) for row in data]
				single = True
			else:
				raise Exception("List Result Set row can have can have minimum 1 and Maximum Two Columns")

			list = List(list_arr)
			list.setSettings({"hasvalues": not single})
			if component.knowmoretext:
				list.setSettings({"knowmoretext": component.knowmoretext})
			return list

		if component.component_type == "Value":
			return data[0][0]

		if component.component_type == "Status":
			return StatusField(data[0], data[1], data[2])

	def getChartData(self, component, ref_doctype, ref_docfield, doc):
		chartModel = self.getDataFromDataSource(component, ref_doctype, ref_docfield,
			doc, component.data_source, component.hook_name)
		settings = {
			"title": component.component_title,
			"type": str(component.chart_type).lower(),  # axis-mixed, or 'bar', 'line', 'pie', 'percentage'
			"height": component.height if component.height and component.height > 0 else 300,
			# "colors": ['purple', '#ffa3ef', 'light-blue']
		}
		chartModel.setSettings(settings)
		return chartModel.generateChartModelObject()

	def getTableData(self, component, ref_doctype, ref_docfield, doc):
		table = self.getDataFromDataSource(component, ref_doctype, ref_docfield,
			doc, component.data_source, component.hook_name)
		table.setSettings({"height": component.height if component.height and component.height > 0 else 200})
		return table.generateTableModelObject()

	def getListData(self, component, ref_doctype, ref_docfield, doc):
		list = self.getDataFromDataSource(component, ref_doctype, ref_docfield,
			doc, component.data_source, component.hook_name)
		list.setSettings({"height": component.height if component.height and component.height > 0 else 200})
		return list.generateListModelObject()

	def getStatusData(self, component, ref_doctype, ref_docfield, doc):
		statusField = self.getDataFromDataSource(component, ref_doctype, ref_docfield,
			doc, component.data_source, component.hook_name)
		return statusField.generateStatusfieldObject()

	def getValuesData(self, component, ref_doctype, ref_docfield, doc):
		value = self.getDataFromDataSource(component, ref_doctype, ref_docfield,
			doc, component.data_source, component.hook_name)
		return SummaryValue(value, component.component_title).generateSummaryValueObject()

	# def getPythonScriptResult(self, component, ref_doctype, ref_docfield):
	# 	code = str(component.component_contents)
	# 	function_name = str(ref_docfield).replace("-","")+str(component.component_title).replace(" ","").replace("-","")
	# 	print ("name options:", ref_docfield, component.component_title)
	# 	code = "def "+function_name+"():\n\t"+("\t".join(code.splitlines(True)))
	# 	code_obj = compile(str(code), "component.component_contents", 'exec')
	# 	print ("code_obj", code)
	# 	exec(code_obj, globals(), globals())
	# 	value = eval(function_name+"()")
	# 	return value

	def getTheHook(self, hook, ref_doctype, ref_docfield, doc):
		print("Hook:", hook)
		for app in frappe.get_installed_apps():
			if frappe.get_hooks(app_name=app).get("dashmanager_renders"):
				hook_name = frappe.get_hooks(app_name=app).get("dashmanager_renders")[hook]
				if hook_name:
					h = frappe.get_attr(hook_name[0])
					a = h(doc)
					return a

	def getQueryResult(self, query, component):
		# first validate if the query is ok..
		self.validateQuery(query, component)
		query = frappe.db.sql(query, {}, as_list=True)
		return query

	def validateQuery(self, query, component):
		token = query.strip().lower().split()[0]
		if token in ['alter', 'drop', 'truncate',
			"insert", "desc", "delete", "update"]:
			frappe.throw("Cannot fire a " + token + " Query in component: " +
				str(component.component_title), frappe.PermissionError)

	def checkIfMultipleQuery(self, query):
		return ":::" in str(query) and len(str(query).split(":::")) > 0


@frappe.whitelist()
def get_dashboard(doctype, active_document):
	# frappe.msgprint("dashmanager")
	dash = frappe.get_doc("Dashmanager", {"ref_doctype": doctype})
	dash.active_document = active_document
	return dash.build_components()


@frappe.whitelist()
def get_dashboard_components(doctype, field, doc):
	"""
	for a given dashboard and fields, there will be a single dashmanager record.
	"""
	dashs = frappe.get_all("Dashmanager", filters={"ref_doctype": doctype, "ref_docfield": doctype + "-" + field})
	dash = frappe.get_doc("Dashmanager", dashs[0])
	return dash.build_dashboard_components(doc)


@frappe.whitelist()
def get_dashmanager_docs():
	"""
	this will return all the documents for which the dashmanager has a registered component.
	getting all doctypes from all dashmanagers
	"""
	ref_docs = get_registered_docs_for_dashmanager()
	return {"ref_docs": json.dumps(ref_docs)}


def get_registered_docs_for_dashmanager():
	dash_docs = frappe.get_all("Dashmanager", fields=["dashmanager_type", "ref_doctype"])
	ref_docs = []
	for dash_doc in dash_docs:
		if dash_doc.ref_doctype not in ref_docs:
			ref_docs.append(dash_doc)
	return ref_docs


"""
get list of fields and components for given DocType
"""
@frappe.whitelist()
def get_dashmanager_field_components(doctype, doc):
	if not doctype or not doc:
		return
	fields_list, fields_component_list = get_fields_component_list(doctype, doc)
	return {"fields": json.dumps(fields_list),
		"fields_components": json.dumps(fields_component_list)}


def get_fields_component_list(doctype, doc):
	dashs = frappe.get_all("Dashmanager", filters={"ref_doctype": doctype})
	fields_list = []
	fields_component_list = {}
	for dash in dashs:
		dash_doc = frappe.get_doc("Dashmanager", dash)
		field = str(dash_doc.ref_docfield).split("-")[1]
		fields_list.append(field)
		filtered_components = []
		for c in dash_doc.components:
			component = {"component_title": c.component_title,
				"component_type": c.component_type}
			filtered_components.append(component)
		fields_component_list[field] = filtered_components
	return fields_list, fields_component_list


@frappe.whitelist()
def get_dashmanager_for_page(page):
	dashs = frappe.get_all("Dashmanager", filters={"ref_doctype": page})
	fields_component_list = {}
	for dash in dashs:
		dash_doc = frappe.get_doc("Dashmanager", dash)
		filtered_components = []
		for c in dash_doc.components:
			component = {"component_title": c.component_title,
				"component_type": c.component_type}
			filtered_components.append(component)
		fields_component_list[0] = filtered_components
	return ["dashmanager-content"], fields_component_list


@frappe.whitelist()
def get_dashmanager_components_settings():
	boostrap_setting_dict = get_boostrap_settings()
	icon_settings_dict = get_icon_settings()
	response = {"boostrap_settings": boostrap_setting_dict,
		"icon_settings": icon_settings_dict}
	return json.dumps(response)


def get_boostrap_settings():
	boostrap_setting_dict = {}
	boostrap_settings = frappe.get_all("Dashmanager Component Setting",
		filters={"setting_type": "Bootstrap Class"}, fields=["setting_key", "setting_value"])
	for bsetting in boostrap_settings:
		boostrap_setting_dict[bsetting.setting_key] = bsetting.setting_value
	return boostrap_setting_dict


def get_icon_settings():
	icon_settings_dict = {}
	icon_settings = frappe.get_all("Dashmanager Component Setting",
		filters={"setting_type": "Icon"}, fields=["setting_key", "setting_value"])
	for isetting in icon_settings:
		icon_settings_dict[isetting.setting_key] = isetting.setting_value
	return icon_settings_dict
