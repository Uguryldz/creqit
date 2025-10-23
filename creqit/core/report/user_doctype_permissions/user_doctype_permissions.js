// Copyright (c) 2024, creqit Technologies and contributors
// For license information, please see license.txt

creqit.query_reports["User Doctype Permissions"] = {
	filters: [
		{
			fieldname: "user",
			label: __("User"),
			fieldtype: "Link",
			options: "User",
			reqd: 1,
		},
	],
};
