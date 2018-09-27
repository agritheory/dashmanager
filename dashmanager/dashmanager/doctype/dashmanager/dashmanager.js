// Copyright (c) 2018, AgriTheory and contributors
// For license information, please see license.txt

var dummy_html = "<div class='row' id='testdrag'><div class='col-xs-6' style='cursor: move;cursor: -webkit-grabbing;'>One</div><div class='col-xs-6' style='cursor: move;cursor: -webkit-grabbing;'>Two</div></div>"

var percentage_to_col_mapping = {
	"100%" : "col-xs-12",
	"75%" : "col-xs-9",
	"50%" : "col-xs-6",
	"33%" : "col-xs-4",
	"25%" : "col-xs-3",
}

frappe.ui.form.on("Dashmanager", {
	onload: function(frm) {
		set_queries(frm);
		mapDataGridWithPreview()
		testDragDrop2(frm);
	}
});

function set_queries(frm){
	frm.set_query("ref_docfield", function()  {
		return {"filters": [
			{"dt": frm.doc.ref_doctype}
		]};
	});
}

function mapDataGridWithPreview() {
	var preview_html = ""
	components = cur_frm.doc["components"]

	for (cno in components) {
		title = components[cno].component_title
		type = components[cno].component_type
		size = components[cno].component_size
		idx = "cidx"+components[cno].idx

		preview_html += "<div id='"+idx+"' class='"+percentage_to_col_mapping[size]+"' style='cursor: move;cursor: -webkit-grabbing;border:1px solid; padding:2px'><i class='octicon octicon-tools'  style=''></i>"+title+"("+type+")</div>"
	}

	preview_html = "<div class='row' id='testdrag'>" + preview_html + "</div>";
	$(cur_frm.fields_dict["preview"].wrapper).html(preview_html);
}

function testDragDrop2(frm){
	console.log("Testing Drag Drop")
	// $(frm.fields_dict["preview"].wrapper).html(dummy_html);
	Sortable.create(testdrag, {
		group: 'testdrag',
		animation: 100, 
		onEnd: function (/**Event*/evt) {
			var itemEl = evt.item;  // dragged HTMLElement
			//evt.to;    // target list
			//evt.from;  // previous list
			// evt.oldIndex;  // element's old index within old parent
			// evt.newIndex;  // element's new index within new parent
			console.log ("old and new index",evt.oldIndex, evt.newIndex)
			console.log ("Doc Before:", cur_frm.doc["components"])
			cur_frm.doc["components"][evt.oldIndex].idx = evt.newIndex + 1
			cur_frm.doc["components"][evt.newIndex].idx = evt.oldIndex + 1
			console.log ("Doc Before:", cur_frm.doc["components"])
			// for (td_no in cur_frm.doc["components"]) {
			// 	if (td_no ==evt.oldIndex) {
			// 		console.log("old == new",td_no ,cur_frm.doc["components"][evt.newIndex])
			// 		temp_docs.push( cur_frm.doc["components"][evt.newIndex])
			// 		console.log("Temp Docs",temp_docs)
			// 	}else if (td_no == evt.newIndex) {
			// 		console.log("new == old",td_no,cur_frm.doc["components"][evt.oldIndex])
			// 		temp_docs.push( cur_frm.doc["components"][evt.oldIndex] )
			// 		console.log("Temp Docs",temp_docs)
			// 	}else {
			// 		console.log("Normal")
			// 		temp_docs[td_no] = cur_frm.doc["components"][td_no]
			// 	}
			// }
			// console.log("Docs:",temp_docs)
			// cur_frm.doc["components"] = []
			// cur_frm.doc["components"] = temp_docs
			console.log ("Doc After:", cur_frm.doc["components"])
			// cur_frm.get_field("components").grid.refresh()
			cur_frm.refresh()
			cur_frm.dirty();
		},
	  });

}

function testDragDrop(frm){
	console.log("Testing Drag Drop")
	// $(frm.fields_dict["preview"].wrapper).html(dummy_html);
	Sortable.create(testdrag, {
		group: 'testdrag',
		animation: 100, 
		onEnd: function (/**Event*/evt) {
			var itemEl = evt.item;  // dragged HTMLElement
			//evt.to;    // target list
			//evt.from;  // previous list
			// evt.oldIndex;  // element's old index within old parent
			// evt.newIndex;  // element's new index within new parent
			console.log ("old and new index",evt.oldIndex, evt.newIndex)
			g_rows = cur_frm.get_field("components").grid.grid_rows;
			cur_frm.get_field("components").grid.grid_rows=[]
			
			temp = g_rows[evt.oldIndex]
			g_rows[evt.oldIndex] = g_rows[evt.newIndex]
			g_rows[evt.newIndex] = temp

			g_rows[evt.oldIndex].doc.idx = evt.newIndex + 1 
			g_rows[evt.newIndex].doc.idx = evt.oldIndex + 1

			components_doc_arr = []
			g2_rows = []
			locals[cur_frm.doctype][cur_frm.docname].components=[]
			for (rowno  in g_rows) {
				components_doc_arr[rowno] = g_rows[rowno].doc
				components_doc_arr[rowno].idx = parseInt(rowno) + 1
				console.log("["+rowno+"]", g_rows[rowno].doc)
				// console.log("component: "+cur_frm.get_field("components").grid.grid_rows_by_docname[components_doc_arr[rowno].name])
				locals[cur_frm.doctype][cur_frm.docname].components[rowno] = components_doc_arr[rowno]
			}
			console.log(components_doc_arr)

			cur_frm.get_field("components").grid.grid_rows = g_rows
			
			cur_frm.doc["components"] = []
			cur_frm.doc["components"] = components_doc_arr
			
			
			console.log("Dirty1")
			
			// for (n in cur_frm.doc["components"]) {
			// 	cur_frm.get_field("components").grid.grid_rows_by_docname[cur_frm.doc["components"][n].name].refresh()
			// 	console.log("Refresh")
			// }
			cur_frm.get_field("components").grid.refresh()
			// cur_frm.refresh()
			cur_frm.dirty();
		},
	  });

}

frappe.ui.form.on('Dashmanager Component',{
	components_add:function(frm){
		console.log("added",frm)
		mapDataGridWithPreview()
	},
	components_remove:function(frm){
		console.log("Removed",frm)
		mapDataGridWithPreview()
	},
	components_move:function(frm){
		console.log("move",frm)
		mapDataGridWithPreview()
	} 

});

frappe.ui.form.on('Dashmanager Component','component_title',function(a,b,c){
	mapDataGridWithPreview()
} );

frappe.ui.form.on('Dashmanager Component','component_type',function(a,b,c){
	mapDataGridWithPreview()
} );

frappe.ui.form.on('Dashmanager Component','component_size',function(a,b,c){
	mapDataGridWithPreview()
} );


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
