// Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

creqit.provide("creqit.pages");
creqit.provide("creqit.views");

creqit.views.Factory = class Factory {
	constructor(opts) {
		$.extend(this, opts);
	}

	show() {
		this.route = creqit.get_route();
		this.page_name = creqit.get_route_str();

		if (this.before_show && this.before_show() === false) return;

		if (creqit.pages[this.page_name]) {
			creqit.container.change_to(this.page_name);
			if (this.on_show) {
				this.on_show();
			}
		} else {
			if (this.route[1]) {
				this.make(this.route);
			} else {
				creqit.show_not_found(this.route);
			}
		}
	}

	make_page(double_column, page_name, sidebar_postition) {
		return creqit.make_page(double_column, page_name, sidebar_postition);
	}
};

creqit.make_page = function (double_column, page_name, sidebar_position) {
	if (!page_name) {
		page_name = creqit.get_route_str();
	}

	const page = creqit.container.add_page(page_name);

	creqit.ui.make_app_page({
		parent: page,
		single_column: !double_column,
		sidebar_position: sidebar_position,
	});

	creqit.container.change_to(page_name);
	return page;
};
