// Copyright (c) 2025, creqit Technologies and contributors
// License: MIT. See LICENSE

creqit.ui.form.on('Facebook Lead Ads Settings', {
	refresh(frm) {
		// OAuth2 Authorization Button
		if (frm.doc.enabled && frm.doc.app_id) {
			frm.add_custom_button(__('Authorize with Facebook'), function() {
				authorize_facebook(frm);
			}, __('OAuth2'));
			
			// Token Status Button
			frm.add_custom_button(__('Check Token Status'), function() {
				check_token_status(frm);
			}, __('OAuth2'));
			
			// Test Callback URL Button
			frm.add_custom_button(__('Test Callback URL'), function() {
				test_callback_url(frm);
			}, __('OAuth2'));
			
			// Refresh Token Button
			if (frm.doc.access_token) {
				frm.add_custom_button(__('Refresh Token'), function() {
					refresh_token(frm);
				}, __('OAuth2'));
			}
			
			// Webhook buttons
			if (frm.doc.webhook_callback_url) {
				frm.add_custom_button(__('Copy Callback URL'), function() {
					copy_to_clipboard(frm.doc.webhook_callback_url, 'Callback URL');
				}, __('Webhook'));
				
				frm.add_custom_button(__('Copy Verify Token'), function() {
					copy_to_clipboard(frm.doc.webhook_verify_token, 'Verify Token');
				}, __('Webhook'));
				
				frm.add_custom_button(__('Regenerate Verify Token'), function() {
					regenerate_verify_token(frm);
				}, __('Webhook'));
			}
		}
		
		// Show token expiry warning
		if (frm.doc.token_expiry) {
			let expiry = new Date(frm.doc.token_expiry);
			let now = new Date();
			let days_remaining = Math.floor((expiry - now) / (1000 * 60 * 60 * 24));
			
			if (days_remaining < 0) {
				frm.dashboard.add_indicator(__('Token Expired'), 'red');
				frm.dashboard.set_headline_alert(
					__('Access token has expired. Please authorize again.'),
					'red'
				);
			} else if (days_remaining < 7) {
				frm.dashboard.add_indicator(__('Token Expiring Soon ({0} days)', [days_remaining]), 'orange');
			} else {
				frm.dashboard.add_indicator(__('Token Valid ({0} days)', [days_remaining]), 'green');
			}
		} else if (frm.doc.access_token) {
			frm.dashboard.add_indicator(__('Token Active'), 'green');
		}
	},
	
	
	app_id(frm) {
		if (frm.doc.app_id && !frm.doc.authorization_url) {
			frm.set_value('authorization_url', 'https://www.facebook.com/v24.0/dialog/oauth');
		}
		if (frm.doc.app_id && !frm.doc.access_token_url) {
			frm.set_value('access_token_url', 'https://graph.facebook.com/v24.0/oauth/access_token');
		}
	}
});

function authorize_facebook(frm) {
	creqit.call({
		method: 'creqit.meta.FacebookLeadAds.oauth.get_authorization_url',
		callback: function(r) {
			if (r.message && r.message.authorization_url) {
				let auth_url = r.message.authorization_url;
				
				// Show info dialog
				creqit.msgprint({
					title: __('Facebook Authorization'),
					message: __('You will be redirected to Facebook to authorize the application.') + '<br><br>' +
						'<strong>' + __('Redirect URI:') + '</strong><br>' +
						'<code style="background: #f5f5f5; padding: 5px; display: block; margin: 5px 0;">' + 
						r.message.redirect_uri + '</code><br>' +
						'<small style="color: #666;">' + __('Make sure this URL is added to your Facebook App settings.') + '</small>',
					primary_action: {
						label: __('Authorize Now'),
						action: function() {
							// Open in new window
							let width = 600;
							let height = 700;
							let left = (screen.width - width) / 2;
							let top = (screen.height - height) / 2;
							
							window.open(
								auth_url,
								'Facebook Authorization',
								`width=${width},height=${height},left=${left},top=${top},toolbar=no,menubar=no`
							);
						}
					}
				});
			}
		}
	});
}

function check_token_status(frm) {
	creqit.call({
		method: 'creqit.meta.FacebookLeadAds.oauth.get_token_info',
		callback: function(r) {
			if (r.message) {
				let status = r.message;
				let message = '';
				let indicator = 'blue';
				
				if (!status.has_token) {
					message = __('No access token configured');
					indicator = 'red';
				} else if (status.is_expired) {
					message = __('Token has expired. Please re-authorize.');
					indicator = 'red';
				} else if (status.expires_in_days !== undefined) {
					message = __('Token is valid. Expires in {0} days ({1} seconds)', 
						[status.expires_in_days, status.expires_in_seconds]);
					indicator = status.expires_in_days < 7 ? 'orange' : 'green';
				} else if (status.is_long_lived) {
					message = __('✅ Token is active (long-lived token, no expiry)<br><small style="color: #666;">This is normal for some Facebook tokens.</small>');
					indicator = 'green';
				} else {
					message = __('Token is active');
					indicator = 'green';
				}
				
				creqit.msgprint({
					title: __('Token Status'),
					message: message,
					indicator: indicator
				});
			}
		}
	});
}

function refresh_token(frm) {
	creqit.confirm(
		__('This will redirect you to Facebook to re-authorize. Continue?'),
		function() {
			creqit.call({
				method: 'creqit.meta.FacebookLeadAds.oauth.refresh_token',
				callback: function(r) {
					if (r.message && r.message.authorization_url) {
						window.location.href = r.message.authorization_url;
					}
				}
			});
		}
	);
}

function test_callback_url(frm) {
	// Get site URL
	let site_url = window.location.origin;
	let test_url = site_url + '/api/method/creqit.meta.FacebookLeadAds.oauth.test_callback';
	
	// Open test page in new window
	let width = 800;
	let height = 700;
	let left = (screen.width - width) / 2;
	let top = (screen.height - height) / 2;
	
	window.open(
		test_url,
		'Callback URL Test',
		`width=${width},height=${height},left=${left},top=${top},toolbar=no,menubar=no`
	);
}

function copy_to_clipboard(text, label) {
	navigator.clipboard.writeText(text).then(function() {
		creqit.show_alert({
			message: __('{0} copied to clipboard!', [label]),
			indicator: 'green'
		});
	}, function(err) {
		creqit.msgprint(__('Failed to copy: {0}', [err]));
	});
}

function regenerate_verify_token(frm) {
	creqit.confirm(
		__('This will generate a new verify token. You will need to update it in Facebook. Continue?'),
		function() {
		creqit.call({
			method: 'regenerate_verify_token',
			doc: frm.doc,
			callback: function(r) {
				if (r.message) {
					creqit.show_alert({
						message: r.message.message,
						indicator: 'orange'
					});
					frm.reload_doc();
				}
			}
		});
		}
	);
}


// Debug helper - use in console
window.debug_facebook_token = function() {
	creqit.call({
		method: 'creqit.meta.FacebookLeadAds.oauth.get_token_info',
		callback: function(r) {
			console.log('Token Info:', r.message);
			
			// Also check raw document
			creqit.call({
				method: 'creqit.client.get',
				args: {
					doctype: 'Facebook Lead Ads Settings',
					name: 'Facebook Lead Ads Settings'
				},
				callback: function(r2) {
					console.log('Settings Document:', r2.message);
					console.log('Has access_token field:', !!r2.message.access_token);
				}
			});
		}
	});
};

