import requests
import json
import creqit
from creqit import _
from creqit.meta.doctype.meta_settings.meta_settings import MetaSettings

class MetaClient:
    def __init__(self):
        self.settings = MetaSettings.get_settings()
        if not self.settings.access_token:
            creqit.throw(_("Meta access token is not configured"))
            
        self.base_url = "https://graph.facebook.com/v18.0"
        self.access_token = self.settings.access_token
        
    def _make_request(self, endpoint, method="GET", params=None, data=None):
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        if params is None:
            params = {}
            
        # Always include access token in params
        params["access_token"] = self.access_token
        
        try:
            creqit.log_error(f"Making API request to {url}", "Debug info")
            creqit.log_error("Request params", str(params))
            
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, params=params, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, params=params, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
                
            creqit.log_error(f"API response status code: {response.status_code}", "Debug info")
            
            response.raise_for_status()
            response_data = response.json()
            
            # Log the response data for debugging
            creqit.log_error(f"Meta API Response for {endpoint}", str(response_data))
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", {}).get("message", str(e))
                    creqit.log_error("Meta API Error Response", str(error_data))
                except:
                    pass
            creqit.log_error(f"Meta API Error: {error_msg}")
            creqit.throw(_("Failed to communicate with Meta API: {0}").format(error_msg))
            
    def get_campaigns(self, account_id=None):
        """Get all campaigns for an account"""
        params = {
            "fields": "id,name,status,objective,account_id",
            "limit": 100  # Increase limit to get more results
        }
        if account_id:
            params["account_id"] = account_id
            
        return self._make_request("me/campaigns", params=params)
        
    def get_ad_sets(self, campaign_id=None):
        """Get all ad sets for a campaign"""
        params = {
            "fields": "id,name,status,campaign_id,targeting,account_id,start_time,end_time,daily_budget,lifetime_budget,bid_amount,optimization_goal",
            "limit": 100
        }
        if campaign_id:
            params["campaign_id"] = campaign_id
            
        try:
            creqit.log_error("Making API request for ad sets", "Debug info")
            response = self._make_request("me/adsets", params=params)
            creqit.log_error("Meta API Ad Sets Response", str(response))
            
            # Check if response is valid
            if not isinstance(response, dict):
                creqit.log_error("Invalid response type", f"Expected dict, got {type(response)}")
                return {"data": []}
                
            # Check if data field exists
            if "data" not in response:
                creqit.log_error("Missing data field in response", str(response))
                return {"data": []}
                
            # Check if data is a list
            if not isinstance(response["data"], list):
                creqit.log_error("Invalid data field type", f"Expected list, got {type(response['data'])}")
                return {"data": []}
                
            return response
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            creqit.log_error("Error getting ad sets", str(e))
            creqit.log_error("Detailed error traceback", error_details)
            return {"data": []}
        
    def get_ads(self, ad_set_id=None):
        """Get all ads for an ad set"""
        params = {
            "fields": "id,name,status,adset_id,campaign_id,creative,account_id",
            "limit": 100
        }
        if ad_set_id:
            params["adset_id"] = ad_set_id
            
        return self._make_request("me/ads", params=params)
        
    def get_leads(self, ad_id=None, ad_set_id=None, campaign_id=None):
        """Get all leads for an ad, ad set, or campaign"""
        params = {
            "fields": "id,name,email,phone,status,ad_id,adset_id,campaign_id,account_id",
            "limit": 100
        }
        
        if ad_id:
            params["ad_id"] = ad_id
        elif ad_set_id:
            params["adset_id"] = ad_set_id
        elif campaign_id:
            params["campaign_id"] = campaign_id
            
        return self._make_request("me/leads", params=params)
        
    def create_campaign(self, data):
        """Create a new campaign"""
        return self._make_request("me/campaigns", method="POST", data=data)
        
    def update_campaign(self, campaign_id, data):
        """Update an existing campaign"""
        return self._make_request(f"{campaign_id}", method="POST", data=data)
        
    def create_ad_set(self, data):
        """Create a new ad set"""
        return self._make_request("me/adsets", method="POST", data=data)
        
    def update_ad_set(self, ad_set_id, data):
        """Update an existing ad set"""
        return self._make_request(f"{ad_set_id}", method="POST", data=data)
        
    def create_ad(self, data):
        """Create a new ad"""
        return self._make_request("me/ads", method="POST", data=data)
        
    def update_ad(self, ad_id, data):
        """Update an existing ad"""
        return self._make_request(f"{ad_id}", method="POST", data=data)
        
    def get_accounts(self):
        """Get all ad accounts"""
        params = {"fields": "id,name,account_id,account_status,currency,timezone_name"}
        return self._make_request("me/adaccounts", params=params) 