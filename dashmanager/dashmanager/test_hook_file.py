from  doctype.dashmanager.DashComponentsWrappers import * 

def test_hook():
    settings = {
        "type":"ordered",
        "bullets":True,
        "hasvalues":True
    }
    
    list = List([ListItem("One1","Value 1"),ListItem("Two","Value 2"),ListItem("Three","Value 3")])
    list.setSettings(settings)
    return list