// Copyright (c) 2017, creqit Technologies and contributors
// For license information, please see license.txt

creqit.ui.form.on("Role Profile", {
	refresh: function (frm) {
		if (has_common(creqit.user_roles, ["Administrator", "System Manager"])) {
			if (!frm.roles_editor) {
				const role_area = $(frm.fields_dict.roles_html.wrapper);
				frm.roles_editor = new creqit.RoleEditor(role_area, frm);
			}
			frm.roles_editor.show();
		}
	},

	validate: function (frm) {
		if (frm.roles_editor) {
			frm.roles_editor.set_roles_in_table();
		}
	},
});
