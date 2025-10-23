creqit.provide("creqit.model");
creqit.provide("creqit.utils");

/**
 * Opens the Website Meta Tag form if it exists for {route}
 * or creates a new doc and opens the form
 */
creqit.utils.set_meta_tag = function (route) {
	creqit.db.exists("Website Route Meta", route).then((exists) => {
		if (exists) {
			creqit.set_route("Form", "Website Route Meta", route);
		} else {
			// new doc
			const doc = creqit.model.get_new_doc("Website Route Meta");
			doc.__newname = route;
			creqit.set_route("Form", doc.doctype, doc.name);
		}
	});
};
