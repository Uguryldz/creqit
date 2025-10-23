creqit.user_info = function (uid) {
	if (!uid) uid = creqit.session.user;

	let user_info;
	if (!(creqit.boot.user_info && creqit.boot.user_info[uid])) {
		user_info = { fullname: uid || "Unknown" };
	} else {
		user_info = creqit.boot.user_info[uid];
	}

	user_info.abbr = creqit.get_abbr(user_info.fullname);
	user_info.color = creqit.get_palette(user_info.fullname);

	return user_info;
};

creqit.update_user_info = function (user_info) {
	for (let user in user_info) {
		if (creqit.boot.user_info[user]) {
			Object.assign(creqit.boot.user_info[user], user_info[user]);
		} else {
			creqit.boot.user_info[user] = user_info[user];
		}
	}
};

creqit.provide("creqit.user");

$.extend(creqit.user, {
	name: "Guest",
	full_name: function (uid) {
		return uid === creqit.session.user
			? __(
					"You",
					null,
					"Name of the current user. For example: You edited this 5 hours ago."
			  )
			: creqit.user_info(uid).fullname;
	},
	image: function (uid) {
		return creqit.user_info(uid).image;
	},
	abbr: function (uid) {
		return creqit.user_info(uid).abbr;
	},
	has_role: function (rl) {
		if (typeof rl == "string") rl = [rl];
		for (var i in rl) {
			if ((creqit.boot ? creqit.boot.user.roles : ["Guest"]).indexOf(rl[i]) != -1)
				return true;
		}
	},
	get_desktop_items: function () {
		// hide based on permission
		var modules_list = $.map(creqit.boot.allowed_modules, function (icon) {
			var m = icon.module_name;
			var type = creqit.modules[m] && creqit.modules[m].type;

			if (creqit.boot.user.allow_modules.indexOf(m) === -1) return null;

			var ret = null;
			if (type === "module") {
				if (creqit.boot.user.allow_modules.indexOf(m) != -1 || creqit.modules[m].is_help)
					ret = m;
			} else if (type === "page") {
				if (creqit.boot.allowed_pages.indexOf(creqit.modules[m].link) != -1) ret = m;
			} else if (type === "list") {
				if (creqit.model.can_read(creqit.modules[m]._doctype)) ret = m;
			} else if (type === "view") {
				ret = m;
			} else if (type === "setup") {
				if (
					creqit.user.has_role("System Manager") ||
					creqit.user.has_role("Administrator")
				)
					ret = m;
			} else {
				ret = m;
			}

			return ret;
		});

		return modules_list;
	},

	is_report_manager: function () {
		return creqit.user.has_role(["Administrator", "System Manager", "Report Manager"]);
	},

	get_formatted_email: function (email) {
		var fullname = creqit.user.full_name(email);

		if (!fullname) {
			return email;
		} else {
			// to quote or to not
			var quote = "";

			// only if these special characters are found
			// why? To make the output same as that in python!
			if (fullname.search(/[\[\]\\()<>@,:;".]/) !== -1) {
				quote = '"';
			}

			return repl("%(quote)s%(fullname)s%(quote)s <%(email)s>", {
				fullname: fullname,
				email: email,
				quote: quote,
			});
		}
	},

	get_emails: () => {
		return Object.keys(creqit.boot.user_info).map((key) => creqit.boot.user_info[key].email);
	},

	/* Normally creqit.user is an object
	 * having properties and methods.
	 * But in the following case
	 *
	 * if (creqit.user === 'Administrator')
	 *
	 * creqit.user will cast to a string
	 * returning creqit.user.name
	 */
	toString: function () {
		return this.name;
	},
});

creqit.session_alive = true;
$(document).bind("mousemove", function () {
	if (creqit.session_alive === false) {
		$(document).trigger("session_alive");
	}
	creqit.session_alive = true;
	if (creqit.session_alive_timeout) clearTimeout(creqit.session_alive_timeout);
	creqit.session_alive_timeout = setTimeout("creqit.session_alive=false;", 30000);
});
