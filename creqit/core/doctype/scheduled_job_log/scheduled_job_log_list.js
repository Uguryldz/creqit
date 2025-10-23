creqit.listview_settings["Scheduled Job Log"] = {
	onload: function (listview) {
		creqit.require("logtypes.bundle.js", () => {
			creqit.utils.logtypes.show_log_retention_message(cur_list.doctype);
		});
	},
};
