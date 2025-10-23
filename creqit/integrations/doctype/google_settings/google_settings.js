// Copyright (c) 2019, creqit Technologies and contributors
// For license information, please see license.txt

creqit.ui.form.on("Google Settings", {
	refresh: function (frm) {
		frm.dashboard.set_headline(
			__("For more information, {0}.", [
				`<a href='https://creqit.com/docs/user/manual/en/creqit_integration/google_settings'>${__(
					"Click here"
				)}</a>`,
			])
		);
	},
});
