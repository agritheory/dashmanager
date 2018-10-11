# -*- coding: utf-8 -*-
# Copyright (c) 2018, AgriTheory and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.jinja import validate_template  # probably don't need this method, but likely other jinja utilities
import json
from  DashComponentsWrappers import * 
import datetime
import time


class Dashmanager(Document):
	syncTimes = {
		"Hourly":20, #60*60,
		"Daily":30, #24*60*60,
		"Weekly":60 #7*24*60*60
	}
	# validation methods
	def validate(self):
		self.make_custom_script()
		self.validate_duplicates()
		self.validate_components()
	
	def validate_duplicates(self):
		existing_docs = frappe.get_all("Dashmanager", filters={"ref_doctype":self.ref_doctype, "ref_docfield":self.ref_docfield})
		if len (existing_docs) > 0:
			if existing_docs[0].name != self.name: 
				frappe.throw("Cannot have two Dashmanagers for same DocType and Custom Field")
	
	def validate_components(self):
		for component in self.components:
			if component.data_source=="SQL":
				## check the queries of all the Components 
				if component.component_contents:
					self.validateQuery(component.component_contents, component)
			if component.data_source=="Hook":
				self.check_for_blank_hooks(component)
	
	def check_for_blank_hooks(self, component):
		if component.data_source=="Hook":
			if not component.hook_name or component.hook_name=="":
				frappe.throw("Hook name cannot be blank for component: "+str(component.component_title))
		

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
		##print("Printing Components")
		components = []
		#index = 0
		rendered_htmls = []
		boostrap_setting_dict = get_boostrap_settings()
		
		for index,component in enumerate(self.components):
			print ("Cache : ")
			dirty = True
			nowDt = datetime.datetime.now()
			nowTs = time.mktime(nowDt.timetuple())
			if component.cache_this_components_query:
				print("Yes")
				timestamp_delta = self.syncTimes[component.cache_this_components_query]
				print("Delta", timestamp_delta)
				if self.components[index].last_cached:
					thenTs = time.mktime(self.components[index].last_cached.timetuple())
					print("Diff:", str(nowTs-thenTs))
					if nowTs>thenTs and (nowTs-thenTs)<timestamp_delta:
						dirty = False
			rendered_html = ""

			if dirty:
				print ("DIRTY")
				component_obj = {
					"title": component.component_title,
					"type": component.component_type,
					"data": self.getDataForComponent(component.component_type, component, self.ref_doctype, self.ref_docfield),
					"domid":self.ref_docfield+"_"+str(index)
				} ## some fields may not be required. Will remove in future
				
				##print("Data", component_obj["data"])
				template_to_render = self.getTemplateForComponent(component.component_type, component, self.ref_doctype, self.ref_docfield)

				rendered_html = frappe.render_template(template_to_render, {
					"component":component_obj ,
					"componentdatajson" : json.dumps(component_obj["data"]),
					"col_class":boostrap_setting_dict[component.component_size]
					})
				
				self.components[index].cached_data = rendered_html

			else:
				print("NOTDIRTY")
				rendered_html = component.cached_data
			
			rendered_htmls.append(rendered_html)
			
			# components.append({
			# 	"title": component.component_title,
			# 	"type": component.component_type,
			# 	"data": self.getDataForComponent(component.component_type, component, self.ref_doctype, self.ref_docfield),
			# 	"template":self.getTemplateForComponent(component.component_type, component, self.ref_doctype, self.ref_docfield),
			# 	"domid":self.ref_docfield+"_"+str(index)
			# })
			#index+=1
			self.components[index].last_cached = nowDt
		## save the last cache time of each components....
		self.save() 
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
		if type=="Status":
			return "dashmanager/templates/statusfieldtemplate.html"

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
		
		if type=="Status":
			return self.getStatusData(component, ref_doctype, ref_docfield)
	
	def getDataFromDataSource(self, component, ref_doctype, ref_docfield, datasource, hook):
		# if datasource == "Python Script":selec
		# 	return self.getPythonScriptResult( component, ref_doctype, ref_docfield)
		if datasource == "Hook":
			return self.getTheHook(hook)
		elif datasource == "SQL":
			## check if there is a seperator
			query = component.component_contents
			if self.checkIfMultipleQuery(query):
				## get all queries...
				if not component.component_type == "Chart":
					raise Exception("Multiple Queries supported only in ")
				queries = str(query).split(":::")
				data =[]
				for q in queries:
					newrow = []
					for row in self.getQueryResult(q, component):
						newrow.append(row[0])
					data.append(newrow)
				return self.convertSqlToWrapperObjects(component, data)
			else:
				if component.component_type=="Chart":
					data = []
					newrow = []
					for row in self.getQueryResult(component.component_contents, component):
						newrow.append(row[0])
					data.append(newrow)
					return self.convertSqlToWrapperObjects(component, data)	
				else:
					return self.convertSqlToWrapperObjects(component,self.getQueryResult(component.component_contents, component))
		# else: 
		# 	## temperory fail safe
		# 	return self.getDataForComponent(type, component, ref_doctype, ref_docfield)
		pass
	
	def convertSqlToWrapperObjects(self, component, data):
		if component.component_type=="Chart":
			chartModel = ChartModel()
			chartModel.setLabels(ChartLabel(str(component.chart_labels).splitlines(False)))
			dset_names = str(component.dataset_names).splitlines(False)
			hasDataSetNames = (len(dset_names) == len(data))
			for index, row in enumerate(data):
				#print ("Got Row:", row)
				if hasDataSetNames:
					chartModel.addDataSets(ChartDataSet(row , dset_names[index]))
				else:
					chartModel.addDataSets(ChartDataSet(row))
			return chartModel	
			# raise Exception("Not yet supported for SQL")
		
		if component.component_type=="Table":
			table = Table(str(component.table_columns).splitlines(False), data)
			if component.knowmoretext:
				table.setSettings({"knowmoretext": component.knowmoretext}) 
			return table
		
		if component.component_type=="List":
			single = False
			if len(data[0]) ==2:
				list_arr = [ListItem(row[0], row[1]) for row in data]
			elif len(data[0]) ==1:
				list_arr = [ListItem(row[0], None) for row in data]
				single = True
			else:
				raise Exception("List Result Set row can have can have minimum 1 and Maximum Two Columns")
			
			list = List(list_arr)
			list.setSettings({"hasvalues":not single})
			if component.knowmoretext:
				list.setSettings({"knowmoretext": component.knowmoretext}) 
			return list
		
		if component.component_type=="Value":
			return data[0][0]
		
		if component.component_type=="Status":
			return StatusField(data[0],data[1], data[2])


	def getChartData(self, component, ref_doctype, ref_docfield):
		## here the data will come from SQL and not statically
		chartModel = self.getDataFromDataSource(component, ref_doctype, ref_docfield, component.data_source,component.hook_name)
		##print("Got Chart Model:", chartModel)
		settings = {
			"title": component.component_title,
			"type": str(component.chart_type).lower(), ##// axis-mixed, or 'bar', 'line', 'pie', 'percentage'
			"height": component.height if component.height and component.height > 0 else 300,
			"colors": ['purple', '#ffa3ef', 'light-blue']
		}
		chartModel.setSettings(settings)
		return chartModel.generateChartModelObject()


		# chartModel = ChartModel(settings)
		# chartModel.setLabels(ChartLabel(["12am-3am", "3am-6am", "6am-9am", "9am-12pm","12pm-3pm", "3pm-6pm", "6pm-9pm", "9pm-12am"]))
		# chartModel.addDataSets(ChartDataSet("Some Data 1", [25, 40, 30, 35, 8, 52, 17, -4],"bar"))
		# chartModel.addDataSets(ChartDataSet("Some Data 1", [25, 50, -10, 15, 18, 32, 27, 14],"bar"))
		# chartModel.addDataSets(ChartDataSet("Some Data 1", [15, 20, -3, -15, 58, 12, -17, 37],"bar"))

	def getTableData(self, component, ref_doctype, ref_docfield):
		## here the data will come from SQL and not statically
		table = self.getDataFromDataSource(component,ref_doctype, ref_docfield, component.data_source, component.hook_name)
		#return Table(str(component.table_columns).splitlines(False), table).generateTableModelObject()
		table.setSettings({"height":component.height if component.height and component.height > 0 else 200})
		return table.generateTableModelObject()
	
	def getListData(self, component, ref_doctype, ref_docfield):
		list = self.getDataFromDataSource(component, ref_doctype, ref_docfield, component.data_source, component.hook_name)		
		list.setSettings({"height":component.height if component.height and component.height > 0 else 200})
		return list.generateListModelObject()
	
	def getStatusData(self, component, ref_doctype, ref_docfield):
		statusField = self.getDataFromDataSource(component, ref_doctype, ref_docfield, component.data_source, component.hook_name)
		return statusField.generateStatusfieldObject()

	def getValuesData(self, component, ref_doctype, ref_docfield):
		value = self.getDataFromDataSource(component, ref_doctype, ref_docfield, component.data_source, component.hook_name)
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
	
	def getTheHook(self, hook):
		##print("Hook:", hook)
		for app in frappe.get_installed_apps():
			if frappe.get_hooks(app_name=app).get("dashmanager_renders"):
				hook_name = frappe.get_hooks(app_name=app).get("dashmanager_renders")[hook]
				if hook_name:
					h = frappe.get_attr(hook_name[0])
					a = h()
					return a
	
	def getQueryResult(self, query, component):
		## first validate if the query is ok..
		self.validateQuery(query, component)
		query = frappe.db.sql(query, {}, as_list=True)
		return query

	def validateQuery(self, query, component):
		token = query.strip().lower().split()[0]
		if token in ['alter', 'drop', 'truncate',"insert", "desc","delete","update"]:
			frappe.throw("Cannot fire a "+token+" Query in component: "+str(component.component_title), frappe.PermissionError)
	
	def checkIfMultipleQuery(self, query):
		return ":::" in str(query) and len(str(query).split(":::")) > 0
		



@frappe.whitelist()
def get_dashboard(doctype, active_document):
	##frappe.msgprint("dashmanager")
	dash = frappe.get_doc("Dashmanager", {"doctype": doctype})
	dash.active_document = active_document
	return dash.build_components()

@frappe.whitelist()
def get_dashboard_components(doctype, field):
	dashs = frappe.get_all("Dashmanager", filters={"ref_doctype": doctype,"ref_docfield":doctype+"-"+field})
	## for a given dashboard and fields, there will be a single dashmanager record.
	##print("Dashs:",dashs)
	dash = frappe.get_doc("Dashmanager", dashs[0])
	return dash.build_dashboard_components()

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
