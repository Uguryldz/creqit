// Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// provide a namespace
if (!window.creqit) window.creqit = {};

creqit.provide = function (namespace) {
	// docs: create a namespace //
	var nsl = namespace.split(".");
	var parent = window;
	for (var i = 0; i < nsl.length; i++) {
		var n = nsl[i];
		if (!parent[n]) {
			parent[n] = {};
		}
		parent = parent[n];
	}
	return parent;
};

creqit.provide("locals");
creqit.provide("creqit.flags");
creqit.provide("creqit.settings");
creqit.provide("creqit.utils");
creqit.provide("creqit.ui.form");
creqit.provide("creqit.modules");
creqit.provide("creqit.templates");
creqit.provide("creqit.test_data");
creqit.provide("creqit.utils");
creqit.provide("creqit.model");
creqit.provide("creqit.user");
creqit.provide("creqit.session");
creqit.provide("creqit._messages");
creqit.provide("locals.DocType");

// for listviews
creqit.provide("creqit.listview_settings");
creqit.provide("creqit.tour");
creqit.provide("creqit.listview_parent_route");

// constants
window.NEWLINE = "\n";
window.TAB = 9;
window.UP_ARROW = 38;
window.DOWN_ARROW = 40;

// proxy for user globals defined in desk.js

// API globals
window.cur_frm = null;
