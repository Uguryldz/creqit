// Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

creqit.provide("creqit.views.formview");

creqit.views.FormFactory = class FormFactory extends creqit.views.Factory {
	make(route) {
		var doctype = route[1],
			doctype_layout = creqit.router.doctype_layout || doctype;

		if (!creqit.views.formview[doctype_layout]) {
			creqit.model.with_doctype(doctype, () => {
				this.page = creqit.container.add_page(doctype_layout);
				creqit.views.formview[doctype_layout] = this.page;
				this.make_and_show(doctype, route);
			});
		} else {
			this.show_doc(route);
		}

		this.setup_events();
	}

	make_and_show(doctype, route) {
		if (creqit.router.doctype_layout) {
			creqit.model.with_doc("DocType Layout", creqit.router.doctype_layout, () => {
				this.make_form(doctype);
				this.show_doc(route);
			});
		} else {
			this.make_form(doctype);
			this.show_doc(route);
		}
	}

	make_form(doctype) {
		this.page.frm = new creqit.ui.form.Form(
			doctype,
			this.page,
			true,
			creqit.router.doctype_layout
		);
	}

	setup_events() {
		if (!this.initialized) {
			$(document).on("page-change", function () {
				creqit.ui.form.close_grid_form();
			});
		}
		this.initialized = true;
	}

	show_doc(route) {
		var doctype = route[1],
			doctype_layout = creqit.router.doctype_layout || doctype,
			name = route.slice(2).join("/");

		if (creqit.model.new_names[name]) {
			// document has been renamed, reroute
			name = creqit.model.new_names[name];
			creqit.set_route("Form", doctype_layout, name);
			return;
		}

		const doc = creqit.get_doc(doctype, name);
		if (
			doc &&
			creqit.model.get_docinfo(doctype, name) &&
			(doc.__islocal || creqit.model.is_fresh(doc))
		) {
			// is document available and recent?
			this.render(doctype_layout, name);
		} else {
			this.fetch_and_render(doctype, name, doctype_layout);
		}
	}

	fetch_and_render(doctype, name, doctype_layout) {
		creqit.model.with_doc(doctype, name, (name, r) => {
			if (r && r["403"]) return; // not permitted

			if (!(locals[doctype] && locals[doctype][name])) {
				if (name && name.substr(0, 3) === "new") {
					this.render_new_doc(doctype, name, doctype_layout);
				} else {
					creqit.show_not_found();
				}
				return;
			}
			this.render(doctype_layout, name);
		});
	}

	render_new_doc(doctype, name, doctype_layout) {
		const new_name = creqit.model.make_new_doc_and_get_name(doctype, true);
		if (new_name === name) {
			this.render(doctype_layout, name);
		} else {
			creqit.route_flags.replace_route = true;
			creqit.set_route("Form", doctype_layout, new_name);
		}
	}

	render(doctype_layout, name) {
		creqit.container.change_to(doctype_layout);
		creqit.views.formview[doctype_layout].frm.refresh(name);
	}
};
