// Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

creqit.provide("creqit.ui.toolbar");
creqit.provide("creqit.search");

creqit.ui.toolbar.Toolbar = class {
	constructor() {
		$("header").replaceWith(
			creqit.render_template("navbar", {
				avatar: creqit.avatar(creqit.session.user, "avatar-medium"),
				navbar_settings: creqit.boot.navbar_settings,
			})
		);
		$(".dropdown-toggle").dropdown();
		$("#toolbar-user a[href]").click(function () {
			$(this).closest(".dropdown-menu").prev().dropdown("toggle");
		});
		//this.createDropdownAndAppend();
		this.setup_awesomebar();
		this.setup_notifications();
		this.setup_help();
		this.setup_read_only_mode();
		this.setup_announcement_widget();
		this.make();
		
	}
	// createDropdownAndAppend() {
	// 		// Butona tıklama olayını tanımlıyoruz
	// 		$("#load-settings-button").click(function() {
	// 			// creqit boot içerisindeki navbar_settings dizisini kontrol ediyoruz
	// 			const navbarSettings = creqit.boot.navbar_settings;
		
	// 			// Eğer navbar_settings tanımlıysa işlem yapıyoruz
	// 			if (navbarSettings && navbarSettings.settings_dropdown) {
	// 				// İçeriği ekleyeceğimiz div'i seçiyoruz
	// 				const targetDiv = $("#my-content-div");
		
	// 				// settings_dropdown içerisindeki verileri döngüyle işleyip div içerisine ekliyoruz
	// 				navbarSettings.settings_dropdown.forEach(function(item) {
	// 					if (!item.hidden) { // Eğer item.hidden false ise işliyoruz
	// 						let contentHTML = '';
		
	// 						if (item.route) {
	// 							contentHTML = `<a class="dropdown-item" href="${item.route}">${item.item_label}</a>`;
	// 						} else if (item.action) {
	// 							contentHTML = `<button class="btn-reset dropdown-item" onclick="return ${item.action}">${item.item_label}</button>`;
	// 						} else {
	// 							contentHTML = `<div class="dropdown-divider"></div>`;
	// 						}
		
	// 						// Oluşturulan HTML içeriğini div'e ekliyoruz
	// 						targetDiv.append(contentHTML);
	// 					}
	// 				});
	// 			} else {
	// 				console.error("navbar_settings or settings_dropdown not found.");
	// 			}
	// 		});

		
	// }

	make() {
		this.bind_events();
		$(document).trigger("toolbar_setup");
		$(".navbar-brand .app-logo").on("click", () => {
			$(".body-sidebar-container")
				.toggleClass("expanded")
				.find(".edit-sidebar-link")
				.addClass("hidden");

			// show close link
			$(".body-sidebar-container")
				.find(".close-sidebar-link")
				.removeClass("hidden")
				.on("click", () => {
					$(".body-sidebar-container").removeClass("expanded");
				});
		});
	}

	bind_events() {
		// clear all custom menus on page change
		$(document).on("page-change", function () {
			$("header .navbar .custom-menu").remove();
		});

		//focus search-modal on show in mobile view
		$("#search-modal").on("shown.bs.modal", function () {
			var search_modal = $(this);
			setTimeout(function () {
				search_modal.find("#modal-search").focus();
			}, 300);
		});
	}

	setup_read_only_mode() {
		if (!creqit.boot.read_only) return;

		$("header .read-only-banner").tooltip({
			delay: { show: 600, hide: 100 },
			trigger: "hover",
		});
	}

	setup_announcement_widget() {
		let current_announcement = creqit.boot.navbar_settings.announcement_widget;

		if (!current_announcement) return;

		// If an unseen announcement is added, overlook dismiss flag
		if (current_announcement != localStorage.getItem("announcement_widget")) {
			localStorage.removeItem("dismissed_announcement_widget");
			localStorage.setItem("announcement_widget", current_announcement);
		}

		// When an announcement is closed, add dismiss flag
		if (!localStorage.getItem("dismissed_announcement_widget")) {
			let announcement_widget = $(".announcement-widget");
			let close_message = announcement_widget.find(".close-message");
			close_message.on(
				"click",
				() =>
					localStorage.setItem("dismissed_announcement_widget", true) ||
					announcement_widget.addClass("hidden")
			);
		}
	}

	setup_help() {
		if (!creqit.boot.desk_settings.notifications) {
			// hide the help section
			$(".navbar .vertical-bar").removeClass("d-sm-block");
			$(".dropdown-help").removeClass("d-lg-block");
			return;
		}
		creqit.provide("creqit.help");
		creqit.help.show_results = show_results;

		this.search = new creqit.search.SearchDialog();
		creqit.provide("creqit.searchdialog");
		creqit.searchdialog.search = this.search;

		$(".dropdown-help .dropdown-toggle").on("click", function () {
			$(".dropdown-help input").focus();
		});

		$(".dropdown-help .dropdown-menu").on("click", "input, button", function (e) {
			e.stopPropagation();
		});

		$("#input-help").on("keydown", function (e) {
			if (e.which == 13) {
				$(this).val("");
			}
		});

		$(document).on("page-change", function () {
			var $help_links = $(".dropdown-help #help-links");
			$help_links.html("");

			var route = creqit.get_route_str();
			var breadcrumbs = route.split("/");

			var links = [];
			for (let i = 0; i < breadcrumbs.length; i++) {
				var r = route.split("/", i + 1);
				var key = r.join("/");
				var help_links = creqit.help.help_links[key] || [];
				links = $.merge(links, help_links);
			}

			if (links.length === 0) {
				$help_links.next().hide();
			} else {
				$help_links.next().show();
			}

			for (let i = 0; i < links.length; i++) {
				var link = links[i];
				var url = link.url;
				$("<a>", {
					href: url,
					class: "dropdown-item",
					text: __(link.label),
					target: "_blank",
				}).appendTo($help_links);
			}

			$(".dropdown-help .dropdown-menu").on("click", "a", show_results);
		});

		var $result_modal = creqit.get_modal("", "");
		$result_modal.addClass("help-modal");

		$(document).on("click", ".help-modal a", show_results);

		function show_results(e) {
			//edit links
			var href = e.target.href;
			if (href.indexOf("blob") > 0) {
				window.open(href, "_blank");
			}
			var path = $(e.target).attr("data-path");
			if (path) {
				e.preventDefault();
			}
		}
	}

	setup_awesomebar() {
		if (creqit.boot.desk_settings.search_bar) {
			let awesome_bar = new creqit.search.AwesomeBar();
			awesome_bar.setup("#navbar-search");
			$(document).ready(function() {
				let awesome_bar_sidebar = new creqit.search.AwesomeBar();
				awesome_bar_sidebar.setup("#sidebar-search");
			});

			creqit.search.utils.make_function_searchable(
				creqit.utils.generate_tracking_url,
				__("Generate Tracking URL")
			);

			if (creqit.model.can_read("RQ Job")) {
				creqit.search.utils.make_function_searchable(function () {
					creqit.set_route("List", "RQ Job");
				}, __("Background Jobs"));
			}
		}
	}

	setup_notifications() {
		if (creqit.boot.desk_settings.notifications && creqit.session.user !== "Guest") {
			this.notifications = new creqit.ui.Notifications();
		}
	}
};

$.extend(creqit.ui.toolbar, {
	add_dropdown_button: function (parent, label, click, icon) {
		var menu = creqit.ui.toolbar.get_menu(parent);
		if (menu.find("li:not(.custom-menu)").length && !menu.find(".divider").length) {
			creqit.ui.toolbar.add_menu_divider(menu);
		}

		return $(
			'<li class="custom-menu"><a><i class="fa-fw ' + icon + '"></i> ' + label + "</a></li>"
		)
			.insertBefore(menu.find(".divider"))
			.find("a")
			.click(function () {
				click.apply(this);
			});
	},
	get_menu: function (label) {
		return $("#navbar-" + label.toLowerCase());
	},
	add_menu_divider: function (menu) {
		menu = typeof menu == "string" ? creqit.ui.toolbar.get_menu(menu) : menu;

		$('<li class="divider custom-menu"></li>').prependTo(menu);
	},
	add_icon_link(route, icon, index, class_name) {
		let parent_element = $(".navbar-right").get(0);
		let new_element = $(`<li class="${class_name}">
			<a class="btn" href="${route}" title="${creqit.utils.to_title_case(
			class_name,
			true
		)}" aria-haspopup="true" aria-expanded="true">
				<div>
					<i class="octicon ${icon}"></i>
				</div>
			</a>
		</li>`).get(0);

		parent_element.insertBefore(new_element, parent_element.children[index]);
	},
	toggle_full_width() {
		let fullwidth = JSON.parse(localStorage.container_fullwidth || "false");
		fullwidth = !fullwidth;
		localStorage.container_fullwidth = fullwidth;
		creqit.ui.toolbar.set_fullwidth_if_enabled();
		$(document.body).trigger("toggleFullWidth");
	},
	set_fullwidth_if_enabled() {
		let fullwidth = JSON.parse(localStorage.container_fullwidth || "false");
		$(document.body).toggleClass("full-width", fullwidth);
	},
	show_shortcuts(e) {
		e.preventDefault();
		creqit.ui.keys.show_keyboard_shortcut_dialog();
		return false;
	},
});

creqit.ui.toolbar.clear_cache = creqit.utils.throttle(function () {
	creqit.assets.clear_local_storage();
	creqit.xcall("creqit.sessions.clear").then((message) => {
		creqit.show_alert({
			message: message,
			indicator: "info",
		});
		location.reload(true);
	});
}, 10000);

creqit.ui.toolbar.show_about = function () {
	try {
		creqit.ui.misc.about();
	} catch (e) {
		console.log(e);
	}
	return false;
};

creqit.ui.toolbar.route_to_user = function () {
	creqit.set_route("Form", "User", creqit.session.user);
};

creqit.ui.toolbar.view_website = function () {
	let website_tab = window.open();
	website_tab.opener = null;
	website_tab.location = "/index";
};

creqit.ui.toolbar.setup_session_defaults = function () {
	let fields = [];
	creqit.call({
		method: "creqit.core.doctype.session_default_settings.session_default_settings.get_session_default_values",
		callback: function (data) {
			fields = JSON.parse(data.message);
			let perms = creqit.perm.get_perm("Session Default Settings");
			//add settings button only if user is a System Manager or has permission on 'Session Default Settings'
			if (creqit.user_roles.includes("System Manager") || perms[0].read == 1) {
				fields[fields.length] = {
					fieldname: "settings",
					fieldtype: "Button",
					label: __("Settings"),
					click: () => {
						creqit.set_route(
							"Form",
							"Session Default Settings",
							"Session Default Settings"
						);
					},
				};
			}
			creqit.prompt(
				fields,
				function (values) {
					//if default is not set for a particular field in prompt
					fields.forEach(function (d) {
						if (!values[d.fieldname]) {
							values[d.fieldname] = "";
						}
					});
					creqit.call({
						method: "creqit.core.doctype.session_default_settings.session_default_settings.set_session_default_values",
						args: {
							default_values: values,
						},
						callback: function (data) {
							if (data.message == "success") {
								creqit.show_alert({
									message: __("Session Defaults Saved"),
									indicator: "green",
								});
								creqit.ui.toolbar.clear_cache();
							} else {
								creqit.show_alert({
									message: __(
										"An error occurred while setting Session Defaults"
									),
									indicator: "red",
								});
							}
						},
					});
				},
				__("Session Defaults"),
				__("Save")
			);
		},
	});
};
