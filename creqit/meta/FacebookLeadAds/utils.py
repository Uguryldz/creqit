# Copyright (c) 2025, creqit Technologies and contributors
# License: MIT. See LICENSE

import creqit
from creqit import _
import requests
import json
from datetime import datetime, timedelta

def get_facebook_api_url(version="v24.0"):
    """Get Facebook API base URL"""
    return f"https://graph.facebook.com/{version}"

def make_facebook_request(endpoint, access_token, method="GET", data=None, params=None):
    """
    Make a request to Facebook Graph API
    
    Args:
        endpoint: API endpoint (e.g., '/me', '/leadgen_forms')
        access_token: Facebook access token
        method: HTTP method (GET, POST, etc.)
        data: Request body data
        params: URL parameters
    
    Returns:
        dict: API response
    """
    base_url = get_facebook_api_url()
    url = f"{base_url}{endpoint}"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    if params is None:
        params = {}
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
        else:
            response = requests.request(method, url, headers=headers, json=data, params=params, timeout=30)
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        creqit.logger().error(f"Facebook API request failed: {str(e)}")
        creqit.throw(_("Facebook API request failed: {0}").format(str(e)))

def get_user_info(access_token):
    """Get Facebook user information"""
    return make_facebook_request('/me', access_token)

def get_leadgen_forms(access_token, page_id=None):
    """Get lead generation forms"""
    if page_id:
        endpoint = f'/{page_id}/leadgen_forms'
    else:
        endpoint = '/leadgen_forms'
    
    return make_facebook_request(endpoint, access_token)

def get_leadgen_form_leads(access_token, form_id):
    """Get leads from a specific form"""
    endpoint = f'/{form_id}/leads'
    return make_facebook_request(endpoint, access_token)

def get_page_info(access_token, page_id):
    """Get Facebook page information"""
    endpoint = f'/{page_id}'
    return make_facebook_request(endpoint, access_token)

def get_user_pages(access_token):
    """Get user's Facebook pages"""
    endpoint = '/me/accounts'
    return make_facebook_request(endpoint, access_token)

def validate_access_token(access_token):
    """Validate Facebook access token"""
    try:
        result = get_user_info(access_token)
        return {
            'valid': True,
            'user_id': result.get('id'),
            'name': result.get('name'),
            'email': result.get('email')
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }

def get_token_info(access_token):
    """Get detailed token information"""
    try:
        # Get token info from Facebook
        token_info = make_facebook_request('/me', access_token, params={'fields': 'id,name,email'})
        
        # Get token debug info
        debug_info = make_facebook_request('/debug_token', access_token, params={'input_token': access_token})
        
        return {
            'valid': True,
            'user_info': token_info,
            'debug_info': debug_info
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }
