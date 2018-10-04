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