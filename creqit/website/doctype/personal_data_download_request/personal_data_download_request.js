// Copyright (c) 2019, creqit Technologies and contributors
// For license information, please see license.txt

creqit.ui.form.on("Personal Data Download Request", {
	onload: function (frm) {
		if (frm.is_new()) {
			frm.doc.user = creqit.session.user;
		}
	},
});
