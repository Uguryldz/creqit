creqit.listview_settings["Webhook Request Log"] = {
	onload: function (list_view) {
		creqit.require("logtypes.bundle.js", () => {
			creqit.utils.logtypes.show_log_retention_message(list_view.doctype);
		});
	},
};
