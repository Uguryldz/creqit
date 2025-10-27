# Copyright (c) 2025, creqit Technologies and contributors
# License: MIT. See LICENSE

"""
Facebook Lead Ads OAuth2 Flow
Handles OAuth2 authorization and token exchange
"""

import creqit
from creqit import _
from urllib.parse import urlencode
import requests


@creqit.whitelist()
def get_authorization_url():
	"""
	Generate Facebook OAuth2 authorization URL
	Returns URL that user should be redirected to for authorization
	"""
	settings = creqit.get_single("Facebook Lead Ads Settings")
	
	if not settings.enabled:
		creqit.throw(_("Facebook Lead Ads is not enabled"))
	
	if not settings.app_id:
		creqit.throw(_("App ID is not configured"))
	
	# Get site URL for redirect
	site_url = creqit.utils.get_url()
	redirect_uri = f"{site_url}/api/method/creqit.meta.FacebookLeadAds.oauth.callback"
	
	# Generate state for CSRF protection
	state = creqit.generate_hash(length=32)
	
	# Store state in cache for verification
	creqit.cache().set_value(f"facebook_oauth_state_{state}", creqit.session.user, expires_in_sec=600)
	
	# Build authorization URL
	params = {
		"client_id": settings.app_id,
		"redirect_uri": redirect_uri,
		"scope": settings.scope,
		"response_type": "code",
		"state": state
	}
	
	auth_url = f"{settings.authorization_url}?{urlencode(params)}"
	
	return {
		"authorization_url": auth_url,
		"redirect_uri": redirect_uri,
		"state": state
	}


@creqit.whitelist(allow_guest=True)
def callback():
	"""
	OAuth2 callback endpoint
	Handles the redirect from Facebook after user authorization
	"""
	# Get query parameters
	code = creqit.request.args.get("code")
	state = creqit.request.args.get("state")
	error = creqit.request.args.get("error")
	error_description = creqit.request.args.get("error_description")
	
	# Check for errors from Facebook
	if error:
		creqit.respond_as_web_page(
			_("Facebook Authorization Error"),
			f"""
			<div style="max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
				<h2 style="color: #d32f2f;">❌ Authorization Failed</h2>
				<p style="font-size: 16px; color: #666;">
					<strong>Error:</strong> {error}<br>
					{error_description or ''}
				</p>
				<a href="/app/facebook-lead-ads-settings" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px;">
					Return to Settings
				</a>
			</div>
			""",
			success=False
		)
		return
	
	# Check if this is a direct access (not from Facebook)
	if not code or not state:
		creqit.respond_as_web_page(
			_("Facebook OAuth2 Callback Endpoint"),
			"""
			<div style="max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
				<h2 style="color: #ff9800;">⚠️ Invalid Access</h2>
				<p style="font-size: 16px; color: #666;">
					This endpoint is only accessible through Facebook OAuth2 flow.
				</p>
				<div style="margin: 30px 0; padding: 20px; background: #f5f5f5; border-radius: 8px; text-align: left;">
					<h3 style="margin-top: 0; color: #333;">How to authorize:</h3>
					<ol style="color: #666; line-height: 1.8;">
						<li>Go to <strong>Facebook Lead Ads Settings</strong></li>
						<li>Click on <strong>OAuth2 → Authorize with Facebook</strong> button</li>
						<li>You will be redirected to Facebook</li>
						<li>Authorize the application</li>
						<li>You will be redirected back here automatically</li>
					</ol>
				</div>
				<a href="/app/facebook-lead-ads-settings" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px;">
					Go to Settings
				</a>
			</div>
			""",
			success=False
		)
		return
	
	# Verify state (CSRF protection)
	cached_user = creqit.cache().get_value(f"facebook_oauth_state_{state}")
	if not cached_user:
		creqit.respond_as_web_page(
			_("Facebook Authorization Error"),
			"""
			<div style="max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
				<h2 style="color: #d32f2f;">❌ Invalid or Expired State</h2>
				<p style="font-size: 16px; color: #666;">
					The authorization state is invalid or has expired.<br>
					This could happen if:
				</p>
				<ul style="text-align: left; color: #666; max-width: 400px; margin: 20px auto;">
					<li>The authorization request is older than 10 minutes</li>
					<li>The authorization was already completed</li>
					<li>The state parameter was tampered with</li>
				</ul>
				<p style="font-size: 14px; color: #999; margin-top: 30px;">
					Please try authorizing again.
				</p>
				<a href="/app/facebook-lead-ads-settings" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px;">
					Try Again
				</a>
			</div>
			""",
			success=False
		)
		return
	
	# Clear the state from cache
	creqit.cache().delete_value(f"facebook_oauth_state_{state}")
	
	try:
		# Exchange code for access token
		settings = creqit.get_doc("Facebook Lead Ads Settings", "Facebook Lead Ads Settings")
		
		site_url = creqit.utils.get_url()
		redirect_uri = f"{site_url}/api/method/creqit.meta.FacebookLeadAds.oauth.callback"
		
		token_data = exchange_code_for_token(
			code=code,
			redirect_uri=redirect_uri,
			client_id=settings.app_id,
			client_secret=settings.get_password("app_secret"),
			token_url=settings.access_token_url
		)
		
		# Save the access token
		access_token = token_data.get("access_token")
		expires_in = token_data.get("expires_in")
		
		if not access_token:
			creqit.throw(_("No access token received from Facebook"))
		
		# Log for debugging
		creqit.logger().info(f"Facebook OAuth: Received token, expires_in: {expires_in}")
		
		# Update settings with token
		settings.set_access_token(access_token, expires_in)
		
		# Log expiry date after setting
		creqit.logger().info(f"Facebook OAuth: Token expiry set to: {settings.token_expiry}")
		
		# Reload to verify it was saved
		settings.reload()
		
		# Verify token was saved
		if not settings.get_access_token():
			creqit.logger().error("Facebook OAuth: Token was not saved properly")
		
		# Get expiry for display
		expiry = settings.token_expiry
		
		# Show success page with auto-close for popup
		expiry_display = ""
		if expiry:
			# Check if expiry is a datetime object or string
			if hasattr(expiry, 'strftime'):
				expiry_display = f'<p style="margin: 5px 0;"><strong>Expires:</strong> {expiry.strftime("%Y-%m-%d %H:%M:%S")}</p>'
			else:
				expiry_display = f'<p style="margin: 5px 0;"><strong>Expires:</strong> {expiry}</p>'
		else:
			expiry_display = '<p style="margin: 5px 0; color: #666;"><em>Long-lived token (no expiry)</em></p>'
		
		creqit.respond_as_web_page(
			_("Facebook Authorization Successful"),
			f"""
			<div style="max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
				<h2 style="color: #4caf50;">✅ Authorization Successful!</h2>
				<p style="font-size: 16px; color: #666;">
					Your Facebook Lead Ads integration is now connected.
				</p>
				<div style="margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 4px;">
					<p style="margin: 5px 0;"><strong>Access Token:</strong> Saved securely</p>
					{expiry_display}
				</div>
				<p id="countdown" style="font-size: 14px; color: #999;">
					This window will close in <span id="seconds">3</span> seconds...
				</p>
				<a href="/app/facebook-lead-ads-settings" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px;">
					Go to Settings Now
				</a>
			</div>
			<script>
				// Auto-close popup and refresh parent
				var secondsLeft = 3;
				var countdownInterval = setInterval(function() {{
					secondsLeft--;
					var secondsSpan = document.getElementById('seconds');
					if (secondsSpan) {{
						secondsSpan.textContent = secondsLeft;
					}}
					
					if (secondsLeft <= 0) {{
						clearInterval(countdownInterval);
						
						// If this is a popup, close it and refresh parent
						if (window.opener && !window.opener.closed) {{
							try {{
								// Only refresh the form, don't change URL
								if (window.opener.cur_frm) {{
									// Refresh the current form
									window.opener.cur_frm.reload_doc();
								}}
							}} catch(e) {{
								console.log('Could not refresh parent:', e);
							}}
							// Close popup
							setTimeout(function() {{
								window.close();
							}}, 500);
						}} else {{
							// If not a popup, redirect to settings
							window.location.href = '/app/facebook-lead-ads-settings';
						}}
					}}
				}}, 1000);
			</script>
			""",
			success=True
		)
		
	except Exception as e:
		creqit.log_error("Facebook OAuth Callback Error")
		creqit.respond_as_web_page(
			_("Facebook Authorization Error"),
			f"""
			<div style="max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
				<h2 style="color: #d32f2f;">❌ Token Exchange Failed</h2>
				<p style="font-size: 16px; color: #666;">
					{str(e)}
				</p>
				<a href="/app/facebook-lead-ads-settings" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px;">
					Try Again
				</a>
			</div>
			""",
			success=False
		)


def exchange_code_for_token(code, redirect_uri, client_id, client_secret, token_url):
	"""
	Exchange authorization code for access token
	
	Args:
		code: Authorization code from Facebook
		redirect_uri: Redirect URI used in authorization
		client_id: Facebook App ID
		client_secret: Facebook App Secret
		token_url: Token endpoint URL
	
	Returns:
		dict: Token data from Facebook
	"""
	data = {
		"client_id": client_id,
		"client_secret": client_secret,
		"redirect_uri": redirect_uri,
		"code": code
	}
	
	try:
		response = requests.post(token_url, data=data)
		response.raise_for_status()
		
		# Facebook returns different content types
		content_type = response.headers.get("content-type", "")
		
		if "application/json" in content_type:
			return response.json()
		else:
			# Parse query string response
			from urllib.parse import parse_qs
			parsed = parse_qs(response.text)
			return {
				"access_token": parsed.get("access_token", [None])[0],
				"expires_in": parsed.get("expires", [None])[0],
				"token_type": parsed.get("token_type", ["Bearer"])[0]
			}
			
	except requests.exceptions.RequestException as e:
		error_msg = str(e)
		if hasattr(e.response, 'text'):
			error_msg = e.response.text
		creqit.throw(_("Failed to exchange code for token: {0}").format(error_msg))


@creqit.whitelist()
def refresh_token():
	"""
	Refresh the access token if it's expired or about to expire
	Note: Facebook doesn't provide refresh tokens for some grant types
	This will redirect user to re-authorize
	"""
	settings = creqit.get_single("Facebook Lead Ads Settings")
	
	if not settings.enabled:
		creqit.throw(_("Facebook Lead Ads is not enabled"))
	
	# Generate new authorization URL
	auth_data = get_authorization_url()
	
	return {
		"message": _("Please re-authorize to get a new token"),
		"authorization_url": auth_data["authorization_url"]
	}


@creqit.whitelist(allow_guest=True)
def test_callback():
	"""
	Test callback endpoint to verify it's accessible
	"""
	site_url = creqit.utils.get_url()
	callback_url = f"{site_url}/api/method/creqit.meta.FacebookLeadAds.oauth.callback"
	
	creqit.respond_as_web_page(
		_("Facebook OAuth2 Callback Test"),
		f"""
		<div style="max-width: 700px; margin: 50px auto; padding: 20px;">
			<div style="text-align: center; margin-bottom: 30px;">
				<h2 style="color: #4caf50;">✅ Callback Endpoint is Working!</h2>
				<p style="font-size: 16px; color: #666;">
					This endpoint is accessible and ready to receive OAuth2 callbacks from Facebook.
				</p>
			</div>
			
			<div style="padding: 20px; background: #f5f5f5; border-radius: 8px; margin: 20px 0;">
				<h3 style="margin-top: 0; color: #333;">Callback URL:</h3>
				<code style="background: white; padding: 10px; display: block; border-radius: 4px; word-break: break-all;">
					{callback_url}
				</code>
			</div>
			
			<div style="padding: 20px; background: #e3f2fd; border-radius: 8px; margin: 20px 0;">
				<h3 style="margin-top: 0; color: #1976d2;">📝 Add this URL to Facebook App:</h3>
				<ol style="color: #666; line-height: 1.8;">
					<li>Go to <a href="https://developers.facebook.com/apps/" target="_blank">Facebook Developers</a></li>
					<li>Select your app</li>
					<li>Go to <strong>Settings → Basic</strong></li>
					<li>Add the callback URL above to <strong>App Domains</strong></li>
					<li>OR go to <strong>Facebook Login → Settings</strong></li>
					<li>Add to <strong>Valid OAuth Redirect URIs</strong></li>
				</ol>
			</div>
			
			<div style="text-align: center; margin-top: 30px;">
				<a href="/app/facebook-lead-ads-settings" style="display: inline-block; margin: 10px; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px;">
					Go to Settings
				</a>
				<a href="https://developers.facebook.com/apps/" target="_blank" style="display: inline-block; margin: 10px; padding: 10px 20px; background: #4267B2; color: white; text-decoration: none; border-radius: 4px;">
					Facebook Developers
				</a>
			</div>
		</div>
		""",
		success=True
	)


@creqit.whitelist()
def get_token_info():
	"""
	Get information about the current access token
	"""
	settings = creqit.get_single("Facebook Lead Ads Settings")
	
	if not settings.enabled:
		creqit.throw(_("Facebook Lead Ads is not enabled"))
	
	access_token = settings.get_access_token()
	
	if not access_token:
		return {
			"has_token": False,
			"message": _("No access token configured")
		}
	
	token_info = {
		"has_token": True,
		"token_expiry": settings.token_expiry
	}
	
	# Check if token is expired
	if settings.token_expiry:
		from datetime import datetime
		if datetime.now() > settings.token_expiry:
			token_info["is_expired"] = True
			token_info["message"] = _("Token has expired. Please re-authorize.")
		else:
			token_info["is_expired"] = False
			remaining = settings.token_expiry - datetime.now()
			token_info["expires_in_seconds"] = int(remaining.total_seconds())
			token_info["expires_in_days"] = remaining.days
	else:
		# No expiry means long-lived token
		token_info["is_expired"] = False
		token_info["is_long_lived"] = True
		token_info["message"] = _("Token is active (long-lived, no expiry)")
	
	return token_info

