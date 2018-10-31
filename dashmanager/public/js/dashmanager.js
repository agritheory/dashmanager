// need to pass the doc type to the API, so that
// required components, fields and data can be loaded.
// data will be rendered to the charts.

/// fire a call each time this script loads to get all registered docs types fo dash manager so that we have
/// an onload hook in form component of respective doctype.

frappe.provide("dashmanager");

class Dashmanager {
	constructor(){
		this.dashboards = [];
	}
}

var dashmanager = new Dashmanager();
registerDocs(dashmanager);


function registerDocs(dashmanager) {
	frappe.call({
		method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashmanager_docs",
		callback: function(r) {
			if (r.message) {
				let refDocs = JSON.parse(r.message.ref_docs);
				if (refDocs) {
					// register onload call back for form of given doc.
					for(let refDoc in refDocs) {
						registerDashDocForOnLoad(refDocs[refDoc]);
					}
				}
			}
		}
	});
}

function registerDashDocForOnLoad(refDoc) {
	if (refDoc.dashmanager_type == "DocType") {
		// console.log("Registering for:", refDoc.ref_doctype);
		frappe.ui.form.on(refDoc.ref_doctype, {
			onload:onLoadHandlerForDashDocForm
		});
	} else {
		dashmanager.dashboards.push(refDoc.ref_doctype);
		// console.log("Registering Page", refDoc.ref_doctype);
	}
}

function onLoadHandlerForDashDocForm(frm, page) {
	console.log("Loaded Frm", frm);
	frappe.run_serially([
		() => {
			if(frm){
				return getRegisteredFieldsAndComponentsForDashDocType(frm);
			} else {
				return getDashmanagerForPage(page);
			}
		},
		(data) => {
			var fields_components = {};
			if (data && data.fields && data.fields_components){
				fields_components = {
					fields:JSON.parse(data.fields),
					components:JSON.parse(data.fields_components)
				};
				return fields_components;
			} else {
				throw "Cannot fetch Dashmanager Data";
			}
		}
	]).then(fields_components => {
		return renderFields(fields_components, frm);
	}, error => {
		console.log ("Dashmanager error: ", error);
		frappe.throw ("Dashmanager error: " + error);
	})
}

function renderFields(fields_components, frm) {
	return frappe.run_serially([
		() => {
			// for each field render components
			for(let fieldno in fields_components.fields) {
				// render all components for the field.
				console.log("Rendering Field...");
				// renderField(frm != undefined ? frm : cur_page.page.page.title,
				// 	fields_components.fields[fieldno],
				// 	fields_components.components[fields_components.fields[fieldno]],
				// 	frm);
			}
		}
	]);
}

function renderField(frm, field) {
	console.log("renderField");
	return frappe.run_serially([
		() => {
			return frappe.call({
				method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashboard_components",
				args: {
					"doctype": frm != undefined ? frm.doctype : cur_page.page.page.title,
					"field": field,
					"doc": frm != undefined ? frm.doc.name : cur_page.page.page.title
				}
			});
		}]).then(
		(r) => {
			if (r && r.message) {
				$(frm.fields_dict[field].wrapper).html(r.message);
				console.log("rendered")
			}
		}, (error) =>{
			console.log("Error",error)
			frappe.throw("Cannot render Dashmanager components:"+error)
		}
	);

}

function getRegisteredFieldsAndComponentsForDashDocType(frm){
	return frappe.run_serially([
		() => {
			return frappe.call({
				method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashmanager_field_components",
				args: {"doctype": frm.doc.doctype, "doc": frm.doc.name},
				error:function(error) {
					console.log("Error:",error);
				}
			});
		}]).then (r=>{
		console.log("Callback,", r);
		// console.log (r.message)
		if (r.message) {
			return r.message;
		}
	}, error=>{
		console.log("error", error);
	});
}

function getDashmanagerForPage(page){
	return frappe.run_serially([
		() => {
			return frappe.call({
				method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashmanager_for_page",
				args: {"page": page},
				error:function(error) {
					console.log("Error:",error);
				}
			});
		}]).then (r=>{
		console.log("Callback,", r);
		console.log (r.message)
		if (r.message) {
			return r.message;
		}
	}, error=>{
		console.log("error", error);
	});
}

function injectPageDash() {
	let route = frappe.get_route().slice(-1)[0];
	// probably better to wrap this in a proxy/ watcher for the dashmanager content field

	$(document).load(function(){
  	console.log('DOM Ready fired');
		let page  = cur_page.page.page.wrapper;
	});
	// $() => {
	//
	// }
	// console.log(route);
	// if(dashmanager.dashboards.indexOf(route) >= 0){
	//
	// 	if(page.find("[data-fieldname=\"dashmanager-content\"]").length == 0){
	// 		console.log("dashmanager div found");
	// 		handleDSM();
	// 	}
	// } else {
	// 	if(page.find("[data-fieldname=\"dashmanager-content\"]").length > 0){
	// 		console.log("dashmanager should not be here");
	// 		// $(".layout-main-section").unbind("DOMSubtreeModified");
	// 		// var elem = page.find("[data-fieldname=\"dashmanager-content\"]");
	// 		// elem.parentNode.removeChild(elem);
	// 	}
	// }
}

function handleDSM() {
	console.log("prepend here")
	// if(!$("div").find("[data-fieldname=\"dashmanager-content\"]")) {
	// 	$(".layout-main-section").prepend("<div data-fieldname='dashmanager-content'></div>");
	// }
}

frappe.route.on("change", () => {
	injectPageDash();
});

frappe.route.on("app_ready", () => {
	injectPageDash();
});
