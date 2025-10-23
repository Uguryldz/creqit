// Copyright (c) 2020, creqit Technologies and contributors
// For license information, please see license.txt

creqit.ui.form.on("Navbar Settings", {
	after_save: function (frm) {
		creqit.ui.toolbar.clear_cache();
	},
});
