// Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt
/* eslint-disable no-console */

// __('Modules') __('Domains') __('Places') __('Administration') # for translation, don't remove

creqit.start_app = function () {
	if (!creqit.Application) return;
	creqit.assets.check();
	creqit.provide("creqit.app");
	creqit.provide("creqit.desk");
	creqit.app = new creqit.Application();
};

$(document).ready(function () {
	if (!creqit.utils.supportsES6) {
		creqit.msgprint({
			indicator: "red",
			title: __("Browser not supported"),
			message: __(
				"Some of the features might not work in your browser. Please update your browser to the latest version."
			),
		});
	}
	creqit.start_app();
});

creqit.Application = class Application {
	constructor() {
		this.startup();
	}

	startup() {
		creqit.realtime.init();
		creqit.model.init();

		this.load_bootinfo();
		this.load_user_permissions();
		this.make_nav_bar();
		this.make_sidebar();
		this.set_favicon();
		this.set_fullwidth_if_enabled();
		this.add_browser_class();
		this.setup_energy_point_listeners();
		this.setup_copy_doc_listener();
		this.setup_broadcast_listeners();

		creqit.ui.keys.setup();

		this.setup_theme();

		// page container
		this.make_page_container();
		this.setup_tours();
		this.set_route();

		// trigger app startup
		$(document).trigger("startup");
		$(document).trigger("app_ready");

		this.show_notices();
		this.show_notes();

		if (creqit.ui.startup_setup_dialog && !creqit.boot.setup_complete) {
			creqit.ui.startup_setup_dialog.pre_show();
			creqit.ui.startup_setup_dialog.show();
		}

		// listen to build errors
		this.setup_build_events();

		if (creqit.sys_defaults.email_user_password) {
			var email_list = creqit.sys_defaults.email_user_password.split(",");
			for (var u in email_list) {
				if (email_list[u] === creqit.user.name) {
					this.set_password(email_list[u]);
				}
			}
		}

		// REDESIGN-TODO: Fix preview popovers
		this.link_preview = new creqit.ui.LinkPreview();

		creqit.broadcast.emit("boot", {
			csrf_token: creqit.csrf_token,
			user: creqit.session.user,
		});
	}

	make_sidebar() {
		this.sidebar = new creqit.ui.Sidebar({});
	}

	setup_theme() {
		creqit.ui.keys.add_shortcut({
			shortcut: "shift+ctrl+g",
			description: __("Switch Theme"),
			action: () => {
				if (creqit.theme_switcher && creqit.theme_switcher.dialog.is_visible) {
					creqit.theme_switcher.hide();
				} else {
					creqit.theme_switcher = new creqit.ui.ThemeSwitcher();
					creqit.theme_switcher.show();
				}
			},
		});

		creqit.ui.add_system_theme_switch_listener();
		const root = document.documentElement;

		const observer = new MutationObserver(() => {
			creqit.ui.set_theme();
		});
		observer.observe(root, {
			attributes: true,
			attributeFilter: ["data-theme-mode"],
		});

		creqit.ui.set_theme();
	}

	setup_tours() {
		if (
			!window.Cypress &&
			creqit.boot.onboarding_tours &&
			creqit.boot.user.onboarding_status != null
		) {
			let pending_tours = !creqit.boot.onboarding_tours.every(
				(tour) => creqit.boot.user.onboarding_status[tour[0]]?.is_complete
			);
			if (pending_tours && creqit.boot.onboarding_tours.length > 0) {
				creqit.require("onboarding_tours.bundle.js", () => {
					creqit.utils.sleep(1000).then(() => {
						creqit.ui.init_onboarding_tour();
					});
				});
			}
		}
	}

	show_notices() {
		if (creqit.boot.messages) {
			creqit.msgprint(creqit.boot.messages);
		}

		if (creqit.user_roles.includes("System Manager")) {
			// delayed following requests to make boot faster
			setTimeout(() => {
				this.show_change_log();
				this.show_update_available();
			}, 1000);
		}

		if (!creqit.boot.developer_mode) {
			let console_security_message = __(
				"Using this console may allow attackers to impersonate you and steal your information. Do not enter or paste code that you do not understand."
			);
			console.log(`%c${console_security_message}`, "font-size: large");
		}

		creqit.realtime.on("version-update", function () {
			var dialog = creqit.msgprint({
				message: __(
					"The application has been updated to a new version, please refresh this page"
				),
				indicator: "green",
				title: __("Version Updated"),
			});
			dialog.set_primary_action(__("Refresh"), function () {
				location.reload(true);
			});
			dialog.get_close_btn().toggle(false);
		});
	}

	set_route() {
		if (creqit.boot && localStorage.getItem("session_last_route")) {
			creqit.set_route(localStorage.getItem("session_last_route"));
			localStorage.removeItem("session_last_route");
		} else {
			// route to home page
			creqit.router.route();
		}
		creqit.router.on("change", () => {
			$(".tooltip").hide();
		});
	}

	set_password(user) {
		var me = this;
		creqit.call({
			method: "creqit.core.doctype.user.user.get_email_awaiting",
			args: {
				user: user,
			},
			callback: function (email_account) {
				email_account = email_account["message"];
				if (email_account) {
					var i = 0;
					if (i < email_account.length) {
						me.email_password_prompt(email_account, user, i);
					}
				}
			},
		});
	}

	email_password_prompt(email_account, user, i) {
		var me = this;
		const email_id = email_account[i]["email_id"];
		let d = new creqit.ui.Dialog({
			title: __("Password missing in Email Account"),
			fields: [
				{
					fieldname: "password",
					fieldtype: "Password",
					label: __(
						"Please enter the password for: <b>{0}</b>",
						[email_id],
						"Email Account"
					),
					reqd: 1,
				},
				{
					fieldname: "submit",
					fieldtype: "Button",
					label: __("Submit", null, "Submit password for Email Account"),
				},
			],
		});
		d.get_input("submit").on("click", function () {
			//setup spinner
			d.hide();
			var s = new creqit.ui.Dialog({
				title: __("Checking one moment"),
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "checking",
					},
				],
			});
			s.fields_dict.checking.$wrapper.html('<i class="fa fa-spinner fa-spin fa-4x"></i>');
			s.show();
			creqit.call({
				method: "creqit.email.doctype.email_account.email_account.set_email_password",
				args: {
					email_account: email_account[i]["email_account"],
					password: d.get_value("password"),
				},
				callback: function (passed) {
					s.hide();
					d.hide(); //hide waiting indication
					if (!passed["message"]) {
						creqit.show_alert(
							{ message: __("Login Failed please try again"), indicator: "error" },
							5
						);
						me.email_password_prompt(email_account, user, i);
					} else {
						if (i + 1 < email_account.length) {
							i = i + 1;
							me.email_password_prompt(email_account, user, i);
						}
					}
				},
			});
		});
		d.show();
	}
	load_bootinfo() {
		if (creqit.boot) {
			this.setup_workspaces();
			creqit.model.sync(creqit.boot.docs);
			this.check_metadata_cache_status();
			this.set_globals();
			this.sync_pages();
			creqit.router.setup();
			this.setup_moment();
			if (creqit.boot.print_css) {
				creqit.dom.set_style(creqit.boot.print_css, "print-style");
			}
			creqit.user.name = creqit.boot.user.name;
			creqit.router.setup();
		} else {
			this.set_as_guest();
		}
	}

	setup_workspaces() {
		creqit.modules = {};
		creqit.workspaces = {};
		creqit.boot.allowed_workspaces = creqit.boot.sidebar_pages.pages;

		for (let page of creqit.boot.allowed_workspaces || []) {
			creqit.modules[page.module] = page;
			creqit.workspaces[creqit.router.slug(page.name)] = page;
		}
	}

	load_user_permissions() {
		creqit.defaults.load_user_permission_from_boot();

		creqit.realtime.on(
			"update_user_permissions",
			creqit.utils.debounce(() => {
				creqit.defaults.update_user_permissions();
			}, 500)
		);
	}

	check_metadata_cache_status() {
		if (creqit.boot.metadata_version != localStorage.metadata_version) {
			creqit.assets.clear_local_storage();
			creqit.assets.init_local_storage();
		}
	}

	set_globals() {
		creqit.session.user = creqit.boot.user.name;
		creqit.session.logged_in_user = creqit.boot.user.name;
		creqit.session.user_email = creqit.boot.user.email;
		creqit.session.user_fullname = creqit.user_info().fullname;

		creqit.user_defaults = creqit.boot.user.defaults;
		creqit.user_roles = creqit.boot.user.roles;
		creqit.sys_defaults = creqit.boot.sysdefaults;

		creqit.ui.py_date_format = creqit.boot.sysdefaults.date_format
			.replace("dd", "%d")
			.replace("mm", "%m")
			.replace("yyyy", "%Y");
		creqit.boot.user.last_selected_values = {};
	}
	sync_pages() {
		// clear cached pages if timestamp is not found
		if (localStorage["page_info"]) {
			creqit.boot.allowed_pages = [];
			var page_info = JSON.parse(localStorage["page_info"]);
			$.each(creqit.boot.page_info, function (name, p) {
				if (!page_info[name] || page_info[name].modified != p.modified) {
					delete localStorage["_page:" + name];
				}
				creqit.boot.allowed_pages.push(name);
			});
		} else {
			creqit.boot.allowed_pages = Object.keys(creqit.boot.page_info);
		}
		localStorage["page_info"] = JSON.stringify(creqit.boot.page_info);
	}
	set_as_guest() {
		creqit.session.user = "Guest";
		creqit.session.user_email = "";
		creqit.session.user_fullname = "Guest";

		creqit.user_defaults = {};
		creqit.user_roles = ["Guest"];
		creqit.sys_defaults = {};
	}
	make_page_container() {
		if ($("#body").length) {
			$(".splash").remove();
			creqit.temp_container = $("<div id='temp-container' style='display: none;'>").appendTo(
				"body"
			);
			creqit.container = new creqit.views.Container();
		}
	}
	make_nav_bar() {
		// toolbar
		if (creqit.boot && creqit.boot.home_page !== "setup-wizard") {
			creqit.creqit_toolbar = new creqit.ui.toolbar.Toolbar();
		}
	}
	logout() {
		var me = this;
		me.logged_out = true;
		return creqit.call({
			method: "logout",
			callback: function (r) {
				if (r.exc) {
					return;
				}
				me.redirect_to_login();
			},
		});
	}
	handle_session_expired() {
		creqit.app.redirect_to_login();
	}
	redirect_to_login() {
		window.location.href = `/login?redirect-to=${encodeURIComponent(
			window.location.pathname + window.location.search
		)}`;
	}
	set_favicon() {
		var link = $('link[type="image/x-icon"]').remove().attr("href");
		$('<link rel="shortcut icon" href="' + link + '" type="image/x-icon">').appendTo("head");
		$('<link rel="icon" href="' + link + '" type="image/x-icon">').appendTo("head");
	}
	trigger_primary_action() {
		// to trigger change event on active input before triggering primary action
		$(document.activeElement).blur();
		// wait for possible JS validations triggered after blur (it might change primary button)
		setTimeout(() => {
			if (window.cur_dialog && cur_dialog.display && !cur_dialog.is_minimized) {
				// trigger primary
				cur_dialog.get_primary_btn().trigger("click");
			} else if (cur_frm && cur_frm.page.btn_primary.is(":visible")) {
				cur_frm.page.btn_primary.trigger("click");
			} else if (creqit.container.page.save_action) {
				creqit.container.page.save_action();
			}
		}, 100);
	}

	show_change_log() {
		var me = this;
		let change_log = creqit.boot.change_log;

		// creqit.boot.change_log = [{
		// 	"change_log": [
		// 		[<version>, <change_log in markdown>],
		// 		[<version>, <change_log in markdown>],
		// 	],
		// 	"description": "ERP made simple",
		// 	"title": "creqit",
		// 	"version": "12.2.0"
		// }];

		if (
			!Array.isArray(change_log) ||
			!change_log.length ||
			window.Cypress ||
			cint(creqit.boot.sysdefaults.disable_change_log_notification)
		) {
			return;
		}

		// Iterate over changelog
		var change_log_dialog = creqit.msgprint({
			message: creqit.render_template("change_log", { change_log: change_log }),
			title: __("Updated To A New Version 🎉"),
			wide: true,
		});
		change_log_dialog.keep_open = true;
		change_log_dialog.custom_onhide = function () {
			creqit.call({
				method: "creqit.utils.change_log.update_last_known_versions",
			});
			me.show_notes();
		};
	}

	show_update_available() {
		if (!creqit.boot.has_app_updates) return;
		creqit.xcall("creqit.utils.change_log.show_update_popup");
	}

	add_browser_class() {
		$("html").addClass(creqit.utils.get_browser().name.toLowerCase());
	}

	set_fullwidth_if_enabled() {
		creqit.ui.toolbar.set_fullwidth_if_enabled();
	}

	show_notes() {
		var me = this;
		if (creqit.boot.notes.length) {
			creqit.boot.notes.forEach(function (note) {
				if (!note.seen || note.notify_on_every_login) {
					var d = creqit.msgprint({ message: note.content, title: note.title });
					d.keep_open = true;
					d.custom_onhide = function () {
						note.seen = true;

						// Mark note as read if the Notify On Every Login flag is not set
						if (!note.notify_on_every_login) {
							creqit.call({
								method: "creqit.desk.doctype.note.note.mark_as_seen",
								args: {
									note: note.name,
								},
							});
						}

						// next note
						me.show_notes();
					};
				}
			});
		}
	}

	setup_build_events() {
		if (creqit.boot.developer_mode) {
			creqit.require("build_events.bundle.js");
		}
	}

	setup_energy_point_listeners() {
		creqit.realtime.on("energy_point_alert", (message) => {
			creqit.show_alert(message);
		});
	}

	setup_copy_doc_listener() {
		$("body").on("paste", (e) => {
			try {
				let pasted_data = creqit.utils.get_clipboard_data(e);
				let doc = JSON.parse(pasted_data);
				if (doc.doctype) {
					e.preventDefault();
					const sleep = creqit.utils.sleep;

					creqit.dom.freeze(__("Creating {0}", [doc.doctype]) + "...");
					// to avoid abrupt UX
					// wait for activity feedback
					sleep(500).then(() => {
						let res = creqit.model.with_doctype(doc.doctype, () => {
							let newdoc = creqit.model.copy_doc(doc);
							newdoc.__newname = doc.name;
							delete doc.name;
							newdoc.idx = null;
							newdoc.__run_link_triggers = false;
							creqit.set_route("Form", newdoc.doctype, newdoc.name);
							creqit.dom.unfreeze();
						});
						res && res.fail?.(creqit.dom.unfreeze);
					});
				}
			} catch (e) {
				//
			}
		});
	}

	/// Setup event listeners for events across browser tabs / web workers.
	setup_broadcast_listeners() {
		// booted in another tab -> refresh csrf to avoid invalid requests.
		creqit.broadcast.on("boot", ({ csrf_token, user }) => {
			if (user && user != creqit.session.user) {
				creqit.msgprint({
					message: __(
						"You've logged in as another user from another tab. Refresh this page to continue using system."
					),
					title: __("User Changed"),
					primary_action: {
						label: __("Refresh"),
						action: () => {
							window.location.reload();
						},
					},
				});
				return;
			}

			if (csrf_token) {
				// If user re-logged in then their other tabs won't be usable without this update.
				creqit.csrf_token = csrf_token;
			}
		});
	}

	setup_moment() {
		moment.updateLocale("en", {
			week: {
				dow: creqit.datetime.get_first_day_of_the_week_index(),
			},
		});
		moment.locale("en");
		moment.user_utc_offset = moment().utcOffset();
		if (creqit.boot.timezone_info) {
			moment.tz.add(creqit.boot.timezone_info);
		}
	}
};

creqit.get_module = function (m, default_module) {
	var module = creqit.modules[m] || default_module;
	if (!module) {
		return;
	}

	if (module._setup) {
		return module;
	}

	if (!module.label) {
		module.label = m;
	}

	if (!module._label) {
		module._label = __(module.label);
	}

	module._setup = true;

	return module;
};
