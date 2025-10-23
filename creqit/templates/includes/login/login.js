// login.js
// don't remove this line (used in test)

window.disable_signup = {{ disable_signup and "true" or "false" }};
window.show_footer_on_login = {{ show_footer_on_login and "true" or "false" }};

window.login = {};

window.verify = {};

login.bind_events = function () {
	$(window).on("hashchange", function () {
		login.route();
	});

	$(".form-login").on("submit", function (event) {
		event.preventDefault();
		var args = {};
		args.cmd = "login";
		args.usr = creqit.utils.xss_sanitise(($("#login_email").val() || "").trim());
		args.pwd = $("#login_password").val();
		if (!args.usr || !args.pwd) {
			{# striptags is used to remove newlines, e is used for escaping #}
			creqit.msgprint("{{ _('Both login and password required') | striptags | e }}");
			return false;
		}
		login.call(args, null, "/login");
		return false;
	});

	$(".form-signup").on("submit", function (event) {
		event.preventDefault();
		var args = {};
		args.cmd = "creqit.core.doctype.user.user.sign_up";
		args.email = ($("#signup_email").val() || "").trim();
		args.redirect_to = creqit.utils.sanitise_redirect(creqit.utils.get_url_arg("redirect-to"));
		args.full_name = creqit.utils.xss_sanitise(($("#signup_fullname").val() || "").trim());
		if (!args.email || !validate_email(args.email) || !args.full_name) {
			login.set_status({{ _("Valid email and name required") | tojson }}, 'red');
			return false;
		}
		login.call(args);
		return false;
	});

	$(".form-forgot").on("submit", function (event) {
		event.preventDefault();
		var args = {};
		args.cmd = "creqit.core.doctype.user.user.reset_password";
		args.user = ($("#forgot_email").val() || "").trim();
		if (!args.user) {
			login.set_status({{ _("Valid Login id required.") | tojson }}, 'red');
			return false;
		}
		login.call(args);
		return false;
	});

	$(".form-login-with-email-link").on("submit", function (event) {
		event.preventDefault();
		var args = {};
		args.cmd = "creqit.www.login.send_login_link";
		args.email = ($("#login_with_email_link_email").val() || "").trim();
		if (!args.email) {
			login.set_status({{ _("Valid Login id required.") | tojson }}, 'red');
			return false;
		}
		login.call(args).then(() => {
			login.set_status({{ _("Login link sent to your email") | tojson }}, 'blue');
			$("#login_with_email_link_email").val("");
		}).catch(() => {
			login.set_status({{ _("Send login link") | tojson }}, 'blue');
		});

		return false;
	});

	// $(".toggle-password").click(function () {
	// 	var input = $($(this).attr("toggle"));
	// 	if (input.attr("type") == "password") {
	// 		input.attr("type", "text");
	// 		$(this).text({{ _("Hide") | tojson }})
	// 	} else {
	// 		input.attr("type", "password");
	// 		$(this).text({{ _("Show") | tojson }})
	// 	}
	// });
	//password svg update/*#UPDATES --sevval*/
	$(".toggle-password").click(function () {
		var input = $($(this).attr("toggle"));
		if (input.attr("type") == "password") {
			input.attr("type", "text");
			// Hide metni yerine 'göz kapalı' ikonunu ekleyin
			$(this).html('<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M1.75 10C1.75 10 4.75 4 10 4C15.25 4 18.25 10 18.25 10C18.25 10 15.25 16 10 16C4.75 16 1.75 10 1.75 10Z" stroke="#818898" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M10 12.25C11.2426 12.25 12.25 11.2426 12.25 10C12.25 8.75736 11.2426 7.75 10 7.75C8.75736 7.75 7.75 8.75736 7.75 10C7.75 11.2426 8.75736 12.25 10 12.25Z" stroke="#818898" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'); // Göz açık ikonu
		} else {
			input.attr("type", "password");
			// Show metni yerine 'göz açık' ikonunu ekleyin
			$(this).html('<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.425 4.18002C8.94125 4.05918 9.4698 3.99877 10 4.00002C15.25 4.00002 18.25 10 18.25 10C17.7947 10.8517 17.2518 11.6536 16.63 12.3925M11.59 11.59C11.384 11.8111 11.1356 11.9884 10.8596 12.1114C10.5836 12.2343 10.2857 12.3005 9.98357 12.3058C9.68146 12.3111 9.38137 12.2555 9.10121 12.1424C8.82104 12.0292 8.56654 11.8608 8.35288 11.6471C8.13923 11.4335 7.97079 11.179 7.85763 10.8988C7.74447 10.6186 7.68889 10.3186 7.69423 10.0165C7.69956 9.71434 7.76568 9.4164 7.88866 9.1404C8.01163 8.86441 8.18894 8.61601 8.41 8.41002M14.455 14.455C13.1729 15.4323 11.6118 15.9737 10 16C4.75 16 1.75 10 1.75 10C2.68292 8.26144 3.97685 6.74247 5.545 5.54502L14.455 14.455Z" stroke="#818898" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M1.75 1.75L18.25 18.25" stroke="#818898" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'); // Göz kapalı ikonu
		}
	});//*********** */
	

	{% if ldap_settings and ldap_settings.enabled %}
	$(".btn-ldap-login").on("click", function () {
		var args = {};
		args.cmd = "{{ ldap_settings.method }}";
		args.usr = ($("#login_email").val() || "").trim();
		args.pwd = $("#login_password").val();
		if (!args.usr || !args.pwd) {
			login.set_status({{ _("Both login and password required") | tojson }}, 'red');
			return false;
		}
		login.call(args);
		return false;
	});
	{% endif %}
}


login.route = function () {
	var route = window.location.hash.slice(1);
	if (!route) route = "login";
	route = route.replaceAll("-", "_");
	login[route]();
}

login.reset_sections = function (hide) {
	if (hide || hide === undefined) {
		$("section.for-login").toggle(false);
		$("section.for-email-login").toggle(false);
		$("section.for-forgot").toggle(false);
		$("section.for-login-with-email-link").toggle(false);
		$("section.for-signup").toggle(false);
	}
	$('section:not(.signup-disabled) .indicator').each(function () {
		$(this).removeClass().addClass('indicator').addClass('blue')
			.text($(this).attr('data-text'));
	});
}

login.login = function () {
	login.reset_sections();
	$(".for-login").toggle(true);
}

login.email = function () {
	login.reset_sections();
	$(".for-email-login").toggle(true);
	$("#login_email").focus();
}

login.steptwo = function () {
	login.reset_sections();
	$(".for-login").toggle(true);
	$("#login_email").focus();
}

login.forgot = function () {
	login.reset_sections();
	if ($("#login_email").val()) {
		$("#forgot_email").val($("#login_email").val());
	}
	$(".for-forgot").toggle(true);
	$("#forgot_email").focus();
}

login.login_with_email_link = function () {
	login.reset_sections();
	if ($("#login_email").val()) {
		$("#login_with_email_link_email").val($("#login_email").val());
	}
	$(".for-login-with-email-link").toggle(true);
	$("#login_with_email_link_email").focus();
}

login.signup = function () {
	login.reset_sections();
	$(".for-signup").toggle(true);
	$("#signup_fullname").focus();
}


// Login
login.call = function (args, callback, url="/") {
	login.set_status({{ _("Verifying...") | tojson }}, 'blue');

	return creqit.call({
		type: "POST",
		url: url,
		args: args,
		callback: callback,
		freeze: true,
		statusCode: login.login_handlers
	});
}

login.set_status = function (message, color) {
	$('section:visible .btn-primary').text(message)
	if (color == "red") {
		$('section:visible .page-card-body').addClass("invalid");
	}
}

login.set_invalid = function (message) {
	$(".login-content.page-card").addClass('invalid-login');
	setTimeout(() => {
		$(".login-content.page-card").removeClass('invalid-login');
	}, 500)
	login.set_status(message, 'red');
	$("#login_password").focus();
}

login.login_handlers = (function () {
	var get_error_handler = function (default_message) {
		return function (xhr, data) {
			if (xhr.responseJSON) {
				data = xhr.responseJSON;
			}

			var message = default_message;
			if (data._server_messages) {
				message = ($.map(JSON.parse(data._server_messages || '[]'), function (v) {
					// temp fix for messages sent as dict
					try {
						return JSON.parse(v).message;
					} catch (e) {
						return v;
					}
				}) || []).join('<br>') || default_message;
			}

			if (message === default_message) {
				login.set_invalid(message);
			} else {
				login.reset_sections(false);
			}

		};
	}

	var login_handlers = {
		200: function (data) {
			if (data.message == 'Logged In') {
				login.set_status({{ _("Success") | tojson }}, 'green');
				document.body.innerHTML = `{% include "templates/includes/splash_screen.html" %}`;
				window.location.href = creqit.utils.sanitise_redirect(creqit.utils.get_url_arg("redirect-to")) || data.home_page;
			} else if (data.message == 'Password Reset') {
				window.location.href = creqit.utils.sanitise_redirect(data.redirect_to);
			} else if (data.message == "No App") {
				login.set_status({{ _("Success") | tojson }}, 'green');
				if (localStorage) {
					var last_visited =
						localStorage.getItem("last_visited")
						|| creqit.utils.sanitise_redirect(creqit.utils.get_url_arg("redirect-to"));
					localStorage.removeItem("last_visited");
				}

				if (data.redirect_to) {
					window.location.href = creqit.utils.sanitise_redirect(data.redirect_to);
				}

				if (last_visited && last_visited != "/login") {
					window.location.href = last_visited;
				} else {
					window.location.href = data.home_page;
				}
			} else if (window.location.hash === '#forgot') {
				if (data.message === 'not found') {
					login.set_status({{ _("Not a valid user") | tojson }}, 'red');
				} else if (data.message == 'not allowed') {
					login.set_status({{ _("Not Allowed") | tojson }}, 'red');
				} else if (data.message == 'disabled') {
					login.set_status({{ _("Not Allowed: Disabled User") | tojson }}, 'red');
				} else {
					login.set_status({{ _("Instructions Emailed") | tojson }}, 'green');
				}


			} else if (window.location.hash === '#signup') {
				if (cint(data.message[0]) == 0) {
					login.set_status(data.message[1], 'red');
				} else {
					login.set_status({{ _("Success") | tojson }}, 'green');
					creqit.msgprint(data.message[1])
				}
				//login.set_status(__(data.message), 'green');
			}

			//OTP verification
			if (data.verification && data.message != 'Logged In') {
				login.set_status({{ _("Success") | tojson }}, 'green');

				document.cookie = "tmp_id=" + data.tmp_id;

				if (data.verification.method == 'OTP App') {
					continue_otp_app(data.verification.setup, data.verification.qrcode);
				} else if (data.verification.method == 'SMS') {
					continue_sms(data.verification.setup, data.verification.prompt);
				} else if (data.verification.method == 'Email') {
					continue_email(data.verification.setup, data.verification.prompt);
				}
			}
		},
		401: get_error_handler({{ _("Invalid Login. Try again.") | tojson }}),
		417: get_error_handler({{ _("Oops! Something went wrong.") | tojson }}),
		404: get_error_handler({{ _("User does not exist.") | tojson }}),
		500: get_error_handler({{ _("Something went wrong.") | tojson }})
	};

	return login_handlers;
})();

creqit.ready(function () {

	login.bind_events();
	if (window.show_footer_on_login) {
		$("body .web-footer").show();
	}

	$(".form-signup, .form-forgot, .form-login-with-email-link").removeClass("hide");
	$(document).trigger('login_rendered');
});

var verify_token = function (event) {
	$(".form-verify").on("submit", function (eventx) {
		eventx.preventDefault();
		var args = {};
		args.cmd = "login";
		args.otp = $("#login_token").val();
		args.tmp_id = creqit.get_cookie('tmp_id');
		if (!args.otp) {
			{# striptags is used to remove newlines, e is used for escaping #}
			creqit.msgprint("{{ _('Login token required') | striptags | e }}");
			return false;
		}
		login.call(args);
		return false;
	});
}

var request_otp = function (r) {
	$('.login-content').empty();
	$('.login-content:visible').append(
		`<div id="twofactor_div">
			<form class="form-verify">
				<div class="page-card-head p-0">
					<span class="indicator blue" data-text="Verification">{{ _("Verification") | e }}</span>
				</div>
				<div id="otp_div"></div>
				<input type="text" id="login_token" autocomplete="off" class="form-control" placeholder="{{ _("Verification Code") | e }}" required="">
				<button class="btn btn-sm btn-primary btn-block mt-3" id="verify_token">{{ _("Verify") | e }}</button>
			</form>
		</div>`
	);
	// add event handler for submit button
	verify_token();
	$("#login_token").get(0)?.focus();
}

var continue_otp_app = function (setup, qrcode) {
	request_otp();
	var qrcode_div = $('<div class="text-muted" style="padding-bottom: 15px;"></div>');

	if (setup) {
		direction = $('<div>').attr('id', 'qr_info').text({{ _("Enter Code displayed in OTP App.") | tojson }});
		qrcode_div.append(direction);
		$('#otp_div').prepend(qrcode_div);
	} else {
		direction = $('<div>').attr('id', 'qr_info').text({{ _("OTP setup using OTP App was not completed. Please contact Administrator.") | tojson }});
		qrcode_div.append(direction);
		$('#otp_div').prepend(qrcode_div);
	}
}

var continue_sms = function (setup, prompt) {
	request_otp();
	var sms_div = $('<div class="text-muted" style="padding-bottom: 15px;"></div>');

	if (setup) {
		sms_div.append(prompt)
		$('#otp_div').prepend(sms_div);
	} else {
		direction = $('<div>').attr('id', 'qr_info').html(prompt || {{ _("SMS was not sent. Please contact Administrator.") | tojson }});
		sms_div.append(direction);
		$('#otp_div').prepend(sms_div)
	}
}

var continue_email = function (setup, prompt) {
	request_otp();
	var email_div = $('<div class="text-muted" style="padding-bottom: 15px;"></div>');

	if (setup) {
		email_div.append(prompt)
		$('#otp_div').prepend(email_div);
	} else {
		var direction = $('<div>').attr('id', 'qr_info').html(prompt || {{ _("Verification code email not sent. Please contact Administrator.") | tojson }});
		email_div.append(direction);
		$('#otp_div').prepend(email_div);
	}
}

login.route();
