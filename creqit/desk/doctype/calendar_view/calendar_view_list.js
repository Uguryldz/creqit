creqit.listview_settings["Calendar View"] = {
	button: {
		show(doc) {
			return doc.name;
		},
		get_label() {
			return creqit.utils.icon("calendar", "sm");
		},
		get_description(doc) {
			return __("View {0}", [`${doc.name}`]);
		},
		action(doc) {
			creqit.set_route("List", doc.reference_doctype, "Calendar", doc.name);
		},
	},
};
