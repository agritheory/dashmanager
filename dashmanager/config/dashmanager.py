from frappe import _

def get_data():
	return [
		{
			"label": _("Dashmanager"),
            "icon": "icon-star",
			"items": [
				{
					"type": "doctype",
                    "name": "Dashmanager",
					"label": _("Dashmanager"),

				}
			]
		}
	]
