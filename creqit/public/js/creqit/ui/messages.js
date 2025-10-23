// Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

creqit.provide("creqit.messages");

import "./dialog";

creqit.messages.waiting = function (parent, msg) {
	return $(creqit.messages.get_waiting_message(msg)).appendTo(parent);
};

creqit.messages.get_waiting_message = function (msg) {
	return repl(
		'<div class="msg-box" style="width: 63%; margin: 30px auto;">\
		<p class="text-center">%(msg)s</p></div>',
		{ msg: msg }
	);
};

creqit.throw = function (msg) {
	if (typeof msg === "string") {
		msg = { message: msg, title: __("Error") };
	}
	if (!msg.indicator) msg.indicator = "red";
	creqit.msgprint(msg);
	throw new Error(msg.message);
};

creqit.confirm = function (message, confirm_action, reject_action) {
	var title_text = __("Confirm", null, "Title of confirmation dialog");

	var d = new creqit.ui.Dialog({
		//title: title_text,
		primary_action_label: __("Yes", null, "Approve confirmation dialog"),
		primary_action: () => {
			confirm_action && confirm_action();
			d.hide();
		},
		secondary_action_label: __("No", null, "Dismiss confirmation dialog"),
		secondary_action: () => d.hide(),
	});

	//d.$body.append(`<p class="creqit-confirm-message">${message}</p>`);
	d.$body.append(`
        <div style="text-align: center;">
			<svg width="89" height="89" viewBox="0 0 89 89" fill="none" xmlns="http://www.w3.org/2000/svg">
				<rect x="0.5" y="0.5" width="88" height="88" rx="44" fill="#EFFAF6"/>
				<path d="M38.9116 53.2071L62.6161 29.5L66.2652 33.1465L38.9116 60.5L22.5 44.0884L26.1465 40.4419L38.9116 53.2071Z" fill="#38C793"/>
			</svg>
			<h4 style="margin-top: 24px;">${title_text}</h4> 
            <p class="creqit-confirm-message">${message}</p>
        </div>
    `);
	d.show();

	// flag, used to bind "okay" on enter
	d.confirm_dialog = true;

	// no if closed without primary action
	if (reject_action) {
		d.onhide = () => {
			if (!d.primary_action_fulfilled) {
				reject_action();
			}
		};
	}

	return d;
};

creqit.warn = function (title, message_html, proceed_action, primary_label, is_minimizable) {
	const d = new creqit.ui.Dialog({
		//title: title,
		indicator: "red",
		primary_action_label: primary_label,
		primary_action: () => {
			if (proceed_action) proceed_action();
			d.hide();
		},
		secondary_action_label: __("Cancel", null, "Secondary button in warning dialog"),
		secondary_action: () => d.hide(),
		minimizable: is_minimizable,
	});

	//d.$body.append(`<div class="creqit-confirm-message">${message_html}</div>`);
	d.$body.append(`
        <div style="text-align: center;">
			<svg width="89" height="89" viewBox="0 0 89 89" fill="none" xmlns="http://www.w3.org/2000/svg">
				<rect x="0.5" y="0.5" width="88" height="88" rx="44" fill="#FEF3EB"/>
				<path d="M54.4404 20.5025L68.5 34.5596V54.4404L54.4404 68.5H34.5596L20.5 54.4404V34.5596L34.5596 20.5H54.4404V20.5025ZM41.5312 51.4271V56.3751H46.4792V51.4271H41.5312ZM41.5312 31.6353V46.4792H46.4792V31.6353H41.5312Z" fill="#F17B2C"/>
			</svg>
			<h4 style="margin-top: 24px;">${title}</h4> 
            <p class="creqit-confirm-message">${message_html}</p>
        </div>
    `);
	d.standard_actions.find(".btn-primary").removeClass("btn-primary").addClass("btn-danger");

	d.show();
	return d;
};

creqit.prompt = function (fields, callback, title, primary_label) {
	if (typeof fields === "string") {
		fields = [
			{
				label: fields,
				fieldname: "value",
				fieldtype: "Data",
				reqd: 1,
			},
		];
	}
	if (!$.isArray(fields)) fields = [fields];
	var d = new creqit.ui.Dialog({
		fields: fields,
		title: title || __("Enter Value", null, "Title of prompt dialog"),
	});
	d.set_primary_action(
		primary_label || __("Submit", null, "Primary action of prompt dialog"),
		function () {
			var values = d.get_values();
			if (!values) {
				return;
			}
			d.hide();
			callback(values);
		}
	);
	d.show();
	return d;
};

creqit.msgprint = function (msg, title, is_minimizable) {
	if (!msg) return;

	let data;
	if ($.isPlainObject(msg)) {
		data = msg;
	} else {
		// passed as JSON
		if (typeof msg === "string" && msg.substr(0, 1) === "{") {
			data = JSON.parse(msg);
		} else {
			data = { message: msg, title: title };
		}
	}

	if (!data.indicator) {
		data.indicator = "blue";
	}

	if (data.as_list) {
		const list_rows = data.message.map((m) => `<li>${m}</li>`).join("");
		data.message = `<ul style="padding-left: 20px">${list_rows}</ul>`;
	}

	if (data.as_table) {
		const rows = data.message
			.map((row) => {
				const cols = row.map((col) => `<td>${col}</td>`).join("");
				return `<tr>${cols}</tr>`;
			})
			.join("");
		data.message = `<table class="table table-bordered" style="margin: 0;">${rows}</table>`;
	}

	if (data.message instanceof Array) {
		let messages = data.message;
		const exceptions = messages
			.map((m) => {
				if (typeof m == "string") {
					return JSON.parse(m);
				} else {
					return m;
				}
			})
			.filter((m) => m.raise_exception);

		// only show exceptions if any exceptions exist
		if (exceptions.length) {
			messages = exceptions;
		}

		messages.forEach(function (m) {
			creqit.msgprint(m);
		});
		return;
	}

	if (data.alert || data.toast) {
		creqit.show_alert(data);
		return;
	}

	if (!creqit.msg_dialog) {
		creqit.msg_dialog = new creqit.ui.Dialog({
			title: __("Message"),
			onhide: function () {
				if (creqit.msg_dialog.custom_onhide) {
					creqit.msg_dialog.custom_onhide();
				}
				creqit.msg_dialog.msg_area.empty();
			},
			minimizable: data.is_minimizable || is_minimizable,
		});

		// class "msgprint" is used in tests
		creqit.msg_dialog.msg_area = $('<div class="msgprint">').appendTo(creqit.msg_dialog.body);

		creqit.msg_dialog.clear = function () {
			creqit.msg_dialog.msg_area.empty();
		};

		creqit.msg_dialog.indicator = creqit.msg_dialog.header.find(".indicator");
	}

	// setup and bind an action to the primary button
	if (data.primary_action) {
		if (
			data.primary_action.server_action &&
			typeof data.primary_action.server_action === "string"
		) {
			data.primary_action.action = () => {
				creqit.call({
					method: data.primary_action.server_action,
					args: data.primary_action.args,
					callback() {
						if (data.primary_action.hide_on_success) {
							creqit.hide_msgprint();
						}
					},
				});
			};
		}

		if (
			data.primary_action.client_action &&
			typeof data.primary_action.client_action === "string"
		) {
			let parts = data.primary_action.client_action.split(".");
			let obj = window;
			for (let part of parts) {
				obj = obj[part];
			}
			data.primary_action.action = () => {
				if (typeof obj === "function") {
					obj(data.primary_action.args);
				}
			};
		}

		creqit.msg_dialog.set_primary_action(
			__(data.primary_action.label) || __(data.primary_action_label) || __("Done"),
			data.primary_action.action
		);
	} else {
		if (creqit.msg_dialog.has_primary_action) {
			creqit.msg_dialog.get_primary_btn().addClass("hide");
			creqit.msg_dialog.has_primary_action = false;
		}
	}

	if (data.secondary_action) {
		creqit.msg_dialog.set_secondary_action(data.secondary_action.action);
		creqit.msg_dialog.set_secondary_action_label(
			__(data.secondary_action.label) || __("Close")
		);
	}

	if (data.message == null) {
		data.message = "";
	}

	if (data.message.search(/<br>|<p>|<li>/) == -1) {
		msg = creqit.utils.replace_newlines(data.message);
	}

	var msg_exists = false;
	if (data.clear) {
		creqit.msg_dialog.msg_area.empty();
	} else {
		msg_exists = creqit.msg_dialog.msg_area.html();
	}

	if (data.title || !msg_exists) {
		// set title only if it is explicitly given
		// and no existing title exists
		creqit.msg_dialog.set_title(
			data.title || __("Message", null, "Default title of the message dialog")
		);
	}

	// show / hide indicator
	if (data.indicator) {
		creqit.msg_dialog.indicator.removeClass().addClass("indicator " + data.indicator);
	} else {
		creqit.msg_dialog.indicator.removeClass().addClass("hidden");
	}

	// width
	if (data.wide) {
		// msgprint should be narrower than the usual dialog
		if (creqit.msg_dialog.wrapper.classList.contains("msgprint-dialog")) {
			creqit.msg_dialog.wrapper.classList.remove("msgprint-dialog");
		}
	} else {
		// msgprint should be narrower than the usual dialog
		creqit.msg_dialog.wrapper.classList.add("msgprint-dialog");
	}

	if (msg_exists) {
		creqit.msg_dialog.msg_area.append("<hr>");
		// append a <hr> if another msg already exists
	}

	creqit.msg_dialog.msg_area.append(data.message);

	// make msgprint always appear on top
	creqit.msg_dialog.$wrapper.css("z-index", 2000);
	creqit.msg_dialog.show();

	return creqit.msg_dialog;
};

window.msgprint = creqit.msgprint;

creqit.hide_msgprint = function (instant) {
	// clear msgprint
	if (creqit.msg_dialog && creqit.msg_dialog.msg_area) {
		creqit.msg_dialog.msg_area.empty();
	}
	if (creqit.msg_dialog && creqit.msg_dialog.$wrapper.is(":visible")) {
		if (instant) {
			creqit.msg_dialog.$wrapper.removeClass("fade");
		}
		creqit.msg_dialog.hide();
		if (instant) {
			creqit.msg_dialog.$wrapper.addClass("fade");
		}
	}
};

// update html in existing msgprint
creqit.update_msgprint = function (html) {
	if (!creqit.msg_dialog || (creqit.msg_dialog && !creqit.msg_dialog.$wrapper.is(":visible"))) {
		creqit.msgprint(html);
	} else {
		creqit.msg_dialog.msg_area.html(html);
	}
};

creqit.verify_password = function (callback) {
	creqit.prompt(
		{
			fieldname: "password",
			label: __("Enter your password"),
			fieldtype: "Password",
			reqd: 1,
		},
		function (data) {
			creqit.call({
				method: "creqit.core.doctype.user.user.verify_password",
				args: {
					password: data.password,
				},
				callback: function (r) {
					if (!r.exc) {
						callback();
					}
				},
			});
		},
		__("Verify Password"),
		__("Verify")
	);
};

creqit.show_progress = (title, count, total = 100, description, hide_on_completion = false) => {
	let dialog;
	if (
		creqit.cur_progress &&
		creqit.cur_progress.title === title &&
		creqit.cur_progress.is_visible
	) {
		dialog = creqit.cur_progress;
	} else {
		dialog = new creqit.ui.Dialog({
			title: title,
		});
		dialog.progress = $(`<div>
			<div class="progress">
				<div class="progress-bar"></div>
			</div>
			<p class="description text-muted small"></p>
		</div`).appendTo(dialog.body);
		dialog.progress_bar = dialog.progress.css({ "margin-top": "10px" }).find(".progress-bar");
		dialog.$wrapper.removeClass("fade");
		dialog.show();
		creqit.cur_progress = dialog;
	}
	if (description) {
		dialog.progress.find(".description").text(description);
	}
	dialog.percent = cint((flt(count) * 100) / total);
	dialog.progress_bar.css({ width: dialog.percent + "%" });
	if (hide_on_completion && dialog.percent === 100) {
		// timeout to avoid abrupt hide
		setTimeout(creqit.hide_progress, 500);
	}
	creqit.cur_progress.$wrapper.css("z-index", 2000);
	return dialog;
};

creqit.hide_progress = function () {
	if (creqit.cur_progress) {
		creqit.cur_progress.hide();
		creqit.cur_progress = null;
	}
};

// Floating Message
creqit.show_alert = creqit.toast = function (message, seconds = 7, actions = {}) {
	let indicator_icon_map = {
		orange: "solid-warning",
		yellow: "solid-warning",
		blue: "solid-info",
		green: "solid-success",
		red: "solid-error",
	};

	if (typeof message === "string") {
		message = {
			message: message,
		};
	}

	if (!$("#dialog-container").length) {
		$('<div id="dialog-container"><div id="alert-container"></div></div>').appendTo("body");
	}

	let icon;
	if (message.indicator) {
		icon = indicator_icon_map[message.indicator.toLowerCase()] || "solid-" + message.indicator;
	} else {
		icon = "solid-info";
	}

	const indicator = message.indicator || "blue";

	const div = $(`
		<div class="alert desk-alert ${indicator}" role="alert">
			<div class="alert-message-container">
				<div class="alert-title-container">
					<div>${creqit.utils.icon(icon, "lg")}</div>
					<div class="alert-message">${message.message}</div>
				</div>
				<div class="alert-subtitle">${message.subtitle || ""}</div>
			</div>
			<div class="alert-body" style="display: none"></div>
			<a class="close">${creqit.utils.icon("close-alt")}</a>
		</div>
	`);

	div.hide().appendTo("#alert-container").show();

	if (message.body) {
		div.find(".alert-body").show().html(message.body);
	}

	div.find(".close, button").click(function () {
		div.addClass("out");
		setTimeout(() => div.remove(), 800);
		return false;
	});

	Object.keys(actions).map((key) => {
		div.find(`[data-action=${key}]`).on("click", actions[key]);
	});

	if (seconds > 2) {
		// Delay for animation
		seconds = seconds - 0.8;
	}

	setTimeout(() => {
		div.addClass("out");
		setTimeout(() => div.remove(), 800);
		return false;
	}, seconds * 1000);

	return div;
};
