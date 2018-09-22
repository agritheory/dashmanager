// need to pass the doc type to the API, so that 
// required components, fields and data can be loaded.
// data will be rendered to the charts.

var route_info = frappe.get_route();

var route_type = route_info[0];
var route = route_info[1];

console.log("Dashmanager");
if (route_type=="Form") {
    if (route) {
        console.log ("Fetching Data and components for: ", route)
        frappe.call({
            method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashboard_components",
            callback: function(r) {
                // code snippet
                console.log (r.message)
                if (r.message) {
                    // var component_fields = r.message;
                    // render_components (component_fields, route);
                    var fieldHtml = r.message;
                    render_test(fieldHtml, route)
                }
            }, args: {
                doctype:route
            }, error:function(error) {
                console.log("Error:",error)
            }
        })
        // call the API for fetching the components.

    }
}


function render_test(html, doctype) {
    // just want to see if the chart is getting rendered.
    console.log("Render Test")
    frappe.ui.form.on(doctype,{
        refresh:function(frm) {
            console.log ("rendering the html")
            $(frm.fields_dict["testfield"].wrapper).html(html);
        }
    })
}
// we will not do in this way, but need to put in more structured way.. 
// this is just to get the feel of the flow
function render_components(component_fields, doctype) {
    // array of component fields
    // one field can have multiple components.

    // loop each field.

    frappe.ui.form.on(doctype, {
        refresh: function (frm) {
            console.log("Rendering Template....")
            for (fieldno in component_fields) {
                console.log("renderng field_", component_fields[fieldno]);
                var field_name = component_fields[fieldno].ref_docfield.split("-")[1];
                if (frm.fields_dict[field_name]) {
                    // render all components
                    for (component_no in component_fields[fieldno].components) {
                        console.log ("Working on component:", component_no)
                        console.log("Rendering Templates :", component_fields[fieldno].components[component_no].template)
                        $(frm.fields_dict[field_name].wrapper)
                            .html(frappe.render_template(component_fields[fieldno].components[component_no].template, {
                                component: component_fields[fieldno].components[component_no],
                                componentdatajson : JSON.stringify(component_fields[fieldno].components[component_no].data)
                            }))

                    }
                }
            }
        }
    })
}
