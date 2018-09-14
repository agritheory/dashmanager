console.log ("Hello Custom")

// console.log(frappe.get_route())
frappe.ui.form.on("Item", {
    refresh: function (frm) {
        console.log("Rendering Template....")
        $(frm.fields_dict['test_html'].wrapper)
                .html(frappe.render_template("dashboardtemplate", {
                    heading:"hello"
                }));
    }
})
