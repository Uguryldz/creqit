// Copyright (c) 2019, creqit Technologies and contributors
// For license information, please see license.txt

creqit.ui.form.on("Notification Settings", {
	onload: (frm) => {
		frm.set_query("subscribed_documents", () => {
			return {
				filters: {
					istable: 0,
				},
			};
		});
	},

	refresh: (frm) => {
		if (creqit.user.has_role("System Manager")) {
			frm.add_custom_button(__("Go to Notification Settings List"), () => {
				creqit.set_route("List", "Notification Settings");
			});
		}
	},
});
