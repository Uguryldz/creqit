// Copyright (c) 2022, creqit Technologies and contributors
// For license information, please see license.txt

creqit.ui.form.on("Error Log", {
	refresh: function (frm) {
		frm.disable_save();

		if (frm.doc.reference_doctype && frm.doc.reference_name) {
			frm.add_custom_button(__("Show Related Errors"), function () {
				creqit.set_route("List", "Error Log", {
					reference_doctype: frm.doc.reference_doctype,
					reference_name: frm.doc.reference_name,
				});
			});
			frm.add_custom_button(__("Open reference document"), function () {
				creqit.set_route("Form", frm.doc.reference_doctype, frm.doc.reference_name);
			});
		}
	},
});
