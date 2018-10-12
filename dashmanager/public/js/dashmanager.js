// need to pass the doc type to the API, so that 
// required components, fields and data can be loaded.
// data will be rendered to the charts.

var route_info = frappe.get_route();

var route_type = route_info[0];
var route = route_info[1];

console.log("Dashmanager");

/// fire a call each time this script loads to get all registered docs types fo dash manager so that we have 
/// a on load hook in form component of respective doc type.

//registerDocs()


function registerDocs() {
    console.log ("Getting all doc types")
    frappe.call({
        method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashmanager_docs",
        callback: function(r) {
            console.log ("dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashmanager_docs",r.message)
            if (r.message) {
                // var component_fields = r.message;
                // render_components (component_fields, route);
                refDocs = JSON.parse(r.message.ref_docs)
                if (refDocs) {
                    // register onload call back for form of given doc.
                    registerAllDashDocsForOnLoad(refDocs)
                }
            }
        }
    })
}

function registerAllDashDocsForOnLoad(refDocs) {
    for (refDoc in  refDocs) {
      registerDashDocForOnLoad(refDocs[refDoc])  
    }
}
function registerDashDocForOnLoad(refDoc) {
    console.log("Registerign for:", refDoc)
    frappe.ui.form.on(refDoc,{
        onload:onLoadHandlerForDashDocForm
    });
}

function onLoadHandlerForDashDocForm(frm) {
    console.log("Loaded Frm", frm);
    frappe.run_serially([
        ()=>{
            return getRegisteredFieldsAndComponentsForDashDocType(frm.doctype)
        },
        (data)=>{
            var fields_components = {}
            if (data && data.fields && data.fields_components){
                fields_components = {
                    fields:JSON.parse(data.fields),
                    components:JSON.parse(data.fields_components)
                }
                return fields_components
            }else {
                throw "Cannot fetch Dashmanager Data"
            }
            
        }
    ]).then(fields_components=>{
        return renderFields(fields_components, frm)
    }, error=>{
        console.log ("Dashmanager error: ",error)
        frappe.throw ("Dashmanager error: "+error)
    })

}

function renderFields(fields_components, frm) {
    return frappe.run_serially([
        ()=>{
            // for each field render components
            for (fieldno in fields_components.fields) {
                //render all components for the field.
                console.log("Rendering Field...")
                renderField(frm.doctype,fields_components.fields[fieldno], fields_components.components[fields_components.fields[fieldno]], frm)
            }
        }
    ]);
}

function renderField(doctype,field, components, frm) {
    // not using components as of now... kept for future availability
    return frappe.run_serially([
        () => {
            //call get_dashboard_components with doctype and field as argument.
            return frappe.call({
                method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashboard_components",
                args: {
                    doctype: doctype,
                    field: field
                }
            })
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

function getRegisteredFieldsAndComponentsForDashDocType(doctype){
    return frappe.run_serially([
        () => {
            return frappe.call({
                method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashmanager_field_components",
                args: {
                    doctype:doctype
                }, error:function(error) {
                    console.log("Error:",error)
                }
            })
        }]).then (r=>{
            console.log("Callback,", r)
            // console.log (r.message)
            if (r.message) {
                return r.message
            }
        }, error=>{
            console.log("error", error)

        })
}

// if (route_type=="Form") {
//     if (route) {
//         console.log ("Fetching Data and components for: ", route)
//         frappe.call({
//             method: "dashmanager.dashmanager.doctype.dashmanager.dashmanager.get_dashboard_components",
//             callback: function(r) {
//                 // code snippet
//                 console.log (r.message)
//                 if (r.message) {
//                     // var component_fields = r.message;
//                     // render_components (component_fields, route);
//                     var fieldHtml = r.message;
//                     render_test(fieldHtml, route)
//                 }
//             }, args: {
//                 doctype:route
//             }, error:function(error) {
//                 console.log("Error:",error)
//             }
//         })
//         // call the API for fetching the components.

//     }
// }


// function render_test(html, doctype) {
//     // just want to see if the chart is getting rendered.
//     console.log("Render Test")
//     frappe.ui.form.on(doctype,{
//         onload:function(frm) {
//             console.log ("rendering the html")
//             $(frm.fields_dict["testfield"].wrapper).html(html);
//         }
//     })
// }
// // we will not do in this way, but need to put in more structured way.. 
// // this is just to get the feel of the flow
// function render_components(component_fields, doctype) {
//     // array of component fields
//     // one field can have multiple components.

//     // loop each field.

//     frappe.ui.form.on(doctype, {
//         refresh: function (frm) {
//             console.log("Rendering Template....")
//             for (fieldno in component_fields) {
//                 console.log("renderng field_", component_fields[fieldno]);
//                 var field_name = component_fields[fieldno].ref_docfield.split("-")[1];
//                 if (frm.fields_dict[field_name]) {
//                     // render all components
//                     for (component_no in component_fields[fieldno].components) {
//                         console.log ("Working on component:", component_no)
//                         console.log("Rendering Templates :", component_fields[fieldno].components[component_no].template)
//                         $(frm.fields_dict[field_name].wrapper)
//                             .html(frappe.render_template(component_fields[fieldno].components[component_no].template, {
//                                 component: component_fields[fieldno].components[component_no],
//                                 componentdatajson : JSON.stringify(component_fields[fieldno].components[component_no].data)
//                             }))

//                     }
//                 }
//             }
//         }
//     })
// }
