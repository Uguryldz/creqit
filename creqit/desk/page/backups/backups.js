creqit.pages["backups"].on_page_load = function (wrapper) {
	var page = creqit.ui.make_app_page({
		parent: wrapper,
		title: __("Download Backups"),
		single_column: true,
	});

	page.add_inner_button(__("Set Number of Backups"), function () {
		creqit.set_route("Form", "System Settings");
	});

	page.add_inner_button(__("Download Files Backup"), function () {
		creqit.call({
			method: "creqit.desk.page.backups.backups.schedule_files_backup",
			args: { user_email: creqit.session.user_email },
		});
	});

	page.add_inner_button(__("Get Backup Encryption Key"), function () {
		if (creqit.user.has_role("System Manager")) {
			creqit.verify_password(function () {
				creqit.call({
					method: "creqit.utils.backups.get_backup_encryption_key",
					callback: function (r) {
						creqit.msgprint({
							title: __("Backup Encryption Key"),
							message: __(r.message),
							indicator: "blue",
						});
					},
				});
			});
		} else {
			creqit.msgprint({
				title: __("Error"),
				message: __("System Manager privileges required."),
				indicator: "red",
			});
		}
	});

	creqit.breadcrumbs.add("Setup");

	$(creqit.render_template("backups")).appendTo(page.body.addClass("no-border"));
};
