// Copyright (c) 2018, AgriTheory and contributors
// For license information, please see license.txt

// var dummy_html = "<div class='row' id='previewCanvas'><div class='col-xs-6' style='cursor: move;cursor: -webkit-grabbing;'>One</div><div class='col-xs-6' style='cursor: move;cursor: -webkit-grabbing;'>Two</div></div>"

var percentage_to_col_mapping = {
	"100%" : "col-xs-12",
	"75%" : "col-xs-9",
	"50%" : "col-xs-6",
	"33%" : "col-xs-4",
	"25%" : "col-xs-3",
};

var component_type_icon_map = {
	"List":"octicon octicon-list-ordered",
	"Chart":"octicon octicon-graph",
	"Table":"octicon octicon-ellipsis",
	"Status":"octicon octicon-diff-modified"
};

var settings = {}

frappe.ui.form.on("Dashmanager", {
	onload: frm => {
		set_queries(frm);
		frappe.run_serially([
			()=>{
				return loadDashmanagerComponentSettings()
			},
			(settingsObj)=>{
				settings = settingsObj;
			},
			()=>{
				mapDataGridWithPreview(frm)
			}
		])

	},
	dashmanager_type: frm => {
		if(frm.doc.dashmanager_type == "DocType"){
			change_fieldname_title(frm, "ref_doctype", "DocType");
		}	else if(frm.doc.dashmanager_type == "Page"){
			change_fieldname_title(frm, "ref_doctype", "Page");
		} else if(frm.doc.dashmanager_type == "Module Def"){
			change_fieldname_title(frm, "ref_doctype", "Module Def");
		}
	}
});

function set_queries(frm){
	frm.set_query("ref_docfield", function()  {
		return {"filters": [
			{"dt": frm.doc.ref_doctype}
		]};
	});
}

function loadDashmanagerComponentSettings() {
	return frappe.run_serially([
		function () {
			return frappe.call({
				method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashmanager_components_settings"
			})
		}
	]).then(r=>{
		let settingsObj = {};
		if (r.message){
			console.log("Settings Response", r);
			settingsObj = JSON.parse(r.message);
		}
		console.log("Settings Obj", settingsObj);
		return settingsObj;
	}, error => {
		frappe.throw("Could not load dashmanager settings")
	})
}

function mapDataGridWithPreview(frm) {
	let preview_html = "";
	let components = frm.doc["components"];
	if(components == undefined || components == null){
		return
	}
	for(let cno in components) {
		let title = components[cno].component_title;
		let type = components[cno].component_type;
		let size = components[cno].component_size;
		let idx = "cidx"+components[cno].idx;
		components[cno].col_class = settings.boostrap_settings[size];
		components[cno].icon = settings.icon_settings[type];
		preview_html += "<div id='" + idx + "' class='" + percentage_to_col_mapping[size] +
		" text-center grid-heading-row ' style='cursor: move;cursor: -webkit-grabbing;border:1px solid; \
		padding:2px; height:200px;'><div style='position:absolute; top:50%;left:50%; \
		transform:translateY(-50%) translateX(-50%);'><i class='"
		+ component_type_icon_map[type] + "'  style='font-size:50px'></i><div>"
		+ title + "(" + type + ")</div></div></div>";
	}

	preview_html = "<div class='row' id='previewCanvas'>" + preview_html + "</div>";
	//$(cur_frm.fields_dict["preview"].wrapper).html(preview_html);
	$(frm.fields_dict["preview"].wrapper).html(frappe.render_template("previewtemplate",{
		"previewdivid":"previewCanvas",
		"components": components,
		"percentage_to_col_mapping":settings.boostrap_settings,//percentage_to_col_mapping,
		"component_type_icon_map":settings.icon_settings//component_type_icon_map
	}));
	make_preview_sortable(frm);
}

function make_preview_sortable(frm){
	// $(frm.fields_dict["preview"].wrapper).html(dummy_html);
	Sortable.create(previewCanvas, {
		group: 'previewCanvas',
		animation: 100,
		onEnd: function (/**Event*/evt) {
			var itemEl = evt.item;  // dragged HTMLElement
			if (evt.newIndex < evt.oldIndex) {
				console.log("Case 1");
				frm.doc["components"][evt.oldIndex].idx = frm.doc["components"][evt.newIndex].idx;
				for(let i = evt.newIndex; i < evt.oldIndex; i++) {
					frm.doc["components"][i].idx++;
				}
			}else if(evt.newIndex > evt.oldIndex) {
				frm.doc["components"][evt.oldIndex].idx = frm.doc["components"][evt.newIndex].idx;
				for (var i = evt.oldIndex+1; i <= evt.newIndex; i++) {
					frm.doc["components"][i].idx--;
				}
			}
			frm.refresh();
			frm.dirty();
		},
	});
}

frappe.ui.form.on("Dashmanager Component",{
	components_add: frm => {
		mapDataGridWithPreview(frm);
	},
	components_remove: frm => {
		mapDataGridWithPreview(frm);
	},
	components_move: frm => {
		mapDataGridWithPreview(frm);
	},
	component_title: frm => {
		mapDataGridWithPreview(frm);
	},
	component_type: frm => {
		mapDataGridWithPreview(frm);
	},
	component_size: frm => {
		mapDataGridWithPreview(frm);
	}
});

function change_fieldname_title(frm, fieldname, new_title){
	frm.fields_dict[fieldname].set_label(new_title);
}


// function testDragDrop(frm){
// 	console.log("Testing Drag Drop")
// 	// $(frm.fields_dict["preview"].wrapper).html(dummy_html);
// 	Sortable.create(previewCanvas, {
// 		group: 'previewCanvas',
// 		animation: 100,
// 		onEnd: function (/**Event*/evt) {
// 			var itemEl = evt.item;  // dragged HTMLElement
// 			//evt.to;    // target list
// 			//evt.from;  // previous list
// 			// evt.oldIndex;  // element's old index within old parent
// 			// evt.newIndex;  // element's new index within new parent
// 			console.log ("old and new index",evt.oldIndex, evt.newIndex)
// 			g_rows = cur_frm.get_field("components").grid.grid_rows;
// 			cur_frm.get_field("components").grid.grid_rows=[]

// 			temp = g_rows[evt.oldIndex]
// 			g_rows[evt.oldIndex] = g_rows[evt.newIndex]
// 			g_rows[evt.newIndex] = temp

// 			g_rows[evt.oldIndex].doc.idx = evt.newIndex + 1
// 			g_rows[evt.newIndex].doc.idx = evt.oldIndex + 1

// 			components_doc_arr = []
// 			g2_rows = []
// 			locals[cur_frm.doctype][cur_frm.docname].components=[]
// 			for (rowno  in g_rows) {
// 				components_doc_arr[rowno] = g_rows[rowno].doc
// 				components_doc_arr[rowno].idx = parseInt(rowno) + 1
// 				console.log("["+rowno+"]", g_rows[rowno].doc)
// 				// console.log("component: "+cur_frm.get_field("components").grid.grid_rows_by_docname[components_doc_arr[rowno].name])
// 				locals[cur_frm.doctype][cur_frm.docname].components[rowno] = components_doc_arr[rowno]
// 			}
// 			console.log(components_doc_arr)

// 			cur_frm.get_field("components").grid.grid_rows = g_rows

// 			cur_frm.doc["components"] = []
// 			cur_frm.doc["components"] = components_doc_arr


// 			console.log("Dirty1")

// 			// for (n in cur_frm.doc["components"]) {
// 			// 	cur_frm.get_field("components").grid.grid_rows_by_docname[cur_frm.doc["components"][n].name].refresh()
// 			// 	console.log("Refresh")
// 			// }
// 			cur_frm.get_field("components").grid.refresh()
// 			// cur_frm.refresh()
// 			cur_frm.dirty();
// 		},
// 	  });

// }




// example custom script for dashboard insertion
// frappe.ui.form.on("Item", {
// 	refresh: frm => {
// 		frappe.call({
// 			method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashboard",
// 			args: {"doctype": frm.doc.doctype, "active_document": frm.doc.name}
// 		}).done((r) => {
// 			let populate = document.getElementById(r.message.docfield);
// 			populate.innerHTML = r.message.dashmanager;
// 		}).fail((r) => {
// 			console.log(r);
// 		});
// 	}
// });
