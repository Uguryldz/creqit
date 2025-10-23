// Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

creqit.ui.form.on("DocType", {
	onload: function (frm) {
		if (frm.is_new() && !frm.doc?.fields) {
			creqit.listview_settings["DocType"].new_doctype_dialog();
		}
		frm.call("check_pending_migration");
	},

	before_save: function (frm) {
		let form_builder = creqit.form_builder;
		if (form_builder?.store) {
			let fields = form_builder.store.update_fields();

			// if fields is a string, it means there is an error
			if (typeof fields === "string") {
				creqit.throw(fields);
			}
		}
	},

	after_save: function (frm) {
		if (
			creqit.form_builder &&
			creqit.form_builder.doctype === frm.doc.name &&
			creqit.form_builder.store
		) {
			creqit.form_builder.store.fetch();
		}
	},

	refresh: function (frm) {
		frm.set_query("role", "permissions", function (doc) {
			if (doc.custom && creqit.session.user != "Administrator") {
				return {
					query: "creqit.core.doctype.role.role.role_query",
					filters: [["Role", "name", "!=", "All"]],
				};
			}
		});

		if (creqit.session.user !== "Administrator" || !creqit.boot.developer_mode) {
			if (frm.is_new()) {
				frm.set_value("custom", 1);
			}
			frm.toggle_enable("custom", 0);
			frm.toggle_enable("is_virtual", 0);
			frm.toggle_enable("beta", 0);
		}

		if (!frm.is_new() && !frm.doc.istable) {
			const button_text = frm.doc.issingle
				? __("Go to {0}", [__(frm.doc.name)])
				: __("Go to {0} List", [__(frm.doc.name)]);
			frm.add_custom_button(button_text, () => {
				window.open(`/app/${creqit.router.slug(frm.doc.name)}`);
			});
		}

		const customize_form_link = `<a href="/app/customize-form">${__("Customize Form")}</a>`;
		if (!creqit.boot.developer_mode && !frm.doc.custom) {
			// make the document read-only
			frm.set_read_only();
			frm.dashboard.clear_comment();
			frm.dashboard.add_comment(
				__("DocTypes cannot be modified, please use {0} instead", [customize_form_link]),
				"blue",
				true
			);
		} else if (creqit.boot.developer_mode) {
			frm.dashboard.clear_comment();
			let msg = __(
				"This site is running in developer mode. Any change made here will be updated in code."
			);
			frm.dashboard.add_comment(msg, "yellow", true);
		}

		if (frm.is_new()) {
			frm.events.set_default_permission(frm);
			frm.set_value("default_view", "List");
		} else {
			frm.toggle_enable("engine", 0);
		}

		// set label for "In List View" for child tables
		frm.get_docfield("fields", "in_list_view").label = frm.doc.istable
			? __("In Grid View")
			: __("In List View");

		frm.cscript.autoname(frm);
		frm.cscript.set_naming_rule_description(frm);
		frm.trigger("setup_default_views");

		render_form_builder(frm);
	},

	istable: (frm) => {
		if (frm.doc.istable && frm.is_new()) {
			frm.set_value("default_view", null);
		} else if (!frm.doc.istable && !frm.is_new()) {
			frm.events.set_default_permission(frm);
		}
	},

	set_default_permission: (frm) => {
		if (!(frm.doc.permissions && frm.doc.permissions.length)) {
			frm.add_child("permissions", { role: "System Manager" });
		}
	},

	is_tree: (frm) => {
		frm.trigger("setup_default_views");
	},

	is_calendar_and_gantt: (frm) => {
		frm.trigger("setup_default_views");
	},

	setup_default_views: (frm) => {
		creqit.model.set_default_views_for_doctype(frm.doc.name, frm);
	},

	on_tab_change: (frm) => {
		let current_tab = frm.get_active_tab().label;

		if (current_tab === "Form") {
			frm.footer.wrapper.hide();
			frm.form_wrapper.find(".form-message").hide();
			frm.form_wrapper.addClass("mb-1");
		} else {
			frm.footer.wrapper.show();
			frm.form_wrapper.find(".form-message").show();
			frm.form_wrapper.removeClass("mb-1");
		}
	},
});

creqit.ui.form.on("DocField", {
	form_render(frm, doctype, docname) {
		frm.trigger("setup_fetch_from_fields", doctype, docname);
	},

	fieldtype: function (frm) {
		frm.trigger("max_attachments");
	},

	fields_add: (frm) => {
		frm.trigger("setup_default_views");
	},
});

function render_form_builder(frm) {
	if (creqit.form_builder && creqit.form_builder.doctype === frm.doc.name) {
		creqit.form_builder.setup_page_actions();
		creqit.form_builder.store.fetch();
		return;
	}

	if (creqit.form_builder) {
		creqit.form_builder.wrapper = $(frm.fields_dict["form_builder"].wrapper);
		creqit.form_builder.frm = frm;
		creqit.form_builder.doctype = frm.doc.name;
		creqit.form_builder.customize = false;
		creqit.form_builder.init(true);
		creqit.form_builder.store.fetch();
	} else {
		creqit.require("form_builder.bundle.js").then(() => {
			creqit.form_builder = new creqit.ui.FormBuilder({
				wrapper: $(frm.fields_dict["form_builder"].wrapper),
				frm: frm,
				doctype: frm.doc.name,
				customize: false,
			});
		});
	}
}

extend_cscript(cur_frm.cscript, new creqit.model.DocTypeController({ frm: cur_frm }));
