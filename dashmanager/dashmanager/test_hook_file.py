from  doctype.dashmanager.DashComponentsWrappers import * 
import frappe

def test_hook():
    components_settings = frappe.get_all("Dashmanager Component Setting", filters={"setting_type":"Bootstrap Class"}, fields=["setting_key", "setting_value"])
    settings = {
        "type":"ordered",
        "bullets":True,
        "hasvalues":True
    }
    list_arr = []
    for c_setting in components_settings:
        list_arr.append(ListItem(c_setting.setting_value, c_setting.setting_key))
    
    list = List(list_arr)
    list.setSettings(settings)
    return list

def summary_value_one():
    ## returning the here
    settings = frappe.get_all("Dashmanager Component Setting")
    ## getting total number of values...
    value = len (settings)
    return value

def summary_value_three():
    settings = frappe.get_all("Dashmanager Component Setting",filters={"setting_type":"Icon"})
    ## getting total number of values...
    value = len (settings)
    return value

def summary_value_two():
    settings = frappe.get_all("Dashmanager Component Setting",filters={"setting_type":"Bootstrap Class"})
    ## getting total number of values...
    value = len (settings)
    return value

def chart_hook():
    chartModel = ChartModel()
    chartModel.setLabels(ChartLabel(["12am-3am", "3am-6am", "6am-9am", "9am-12pm","12pm-3pm", "3pm-6pm", "6pm-9pm", "9pm-12am"]))
    chartModel.addDataSets(ChartDataSet([25, 40, 30, 35, 8, 52, 17, -4], "Sales " ))
    chartModel.addDataSets(ChartDataSet([25, 50, -10, 15, 18, 32, 27, 14],"HR"))
    chartModel.addDataSets(ChartDataSet( [15, 20, -3, -15, 58, 12, -17, 37],"Marketing"))
    return chartModel

def status_hooks1():
    return StatusField("Comm Check", "green","LIVE")

def status_hooks2():
    return StatusField("Database", "blue","Stable")

def status_hooks3():
    return StatusField("CPU", "red","Max")

def status_hooks4():
    return StatusField("Developer", "orange","Sick")