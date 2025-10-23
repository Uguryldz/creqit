// Copyright (c) 2017, creqit Technologies and contributors
// For license information, please see license.txt

creqit.ui.form.on("Print Style", {
	refresh: function (frm) {
		frm.add_custom_button(__("Print Settings"), () => {
			creqit.set_route("Form", "Print Settings");
		});
	},
});
