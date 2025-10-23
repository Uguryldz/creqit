creqit.listview_settings["Route History"] = {
	onload: function (listview) {
		creqit.require("logtypes.bundle.js", () => {
			creqit.utils.logtypes.show_log_retention_message(cur_list.doctype);
		});
	},
};
