// Copyright (c) 2018, AgriTheory and contributors
// For license information, please see license.txt

frappe.ui.form.on("Dashmanager", {
	refresh: function(frm) {



	}
});

// example custom script for dashboard insertion
frappe.ui.form.on("Item", {
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
