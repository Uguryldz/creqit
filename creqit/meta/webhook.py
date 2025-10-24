import creqit
from creqit import _
from creqit.meta.doctype.meta_settings.meta_settings import MetaSettings
from creqit.meta.meta_client import MetaClient

def handle_webhook(request_data):
    """Handle incoming webhook from Meta"""
    try:
        settings = MetaSettings.get_settings()
        if not settings.webhook_enabled:
            return {"status": "webhook_disabled"}
            
        # Verify webhook secret
        if request_data.get("secret") != settings.webhook_secret:
            return {"status": "invalid_secret"}
            
        # Process different webhook types
        webhook_type = request_data.get("type")
        if webhook_type == "lead":
            return handle_lead_webhook(request_data)
        elif webhook_type == "campaign":
            return handle_campaign_webhook(request_data)
        elif webhook_type == "ad_set":
            return handle_ad_set_webhook(request_data)
        elif webhook_type == "ad":
            return handle_ad_webhook(request_data)
        else:
            return {"status": "unknown_type"}
            
    except Exception as e:
        creqit.log_error("Meta Webhook Error", str(e))
        return {"status": "error", "message": str(e)}
        
def handle_lead_webhook(data):
    """Handle lead webhook"""
    lead_data = data.get("data", {})
    if not lead_data:
        return {"status": "no_data"}
        
    try:
        # Check if lead exists
        existing = creqit.get_all("Meta Lead", filters={"meta_lead_id": lead_data.get("id")})
        
        lead_doc = {
            "doctype": "Meta Lead",
            "lead_id": lead_data.get("name"),
            "lead_name": lead_data.get("name"),
            "lead_email": lead_data.get("email"),
            "lead_phone": lead_data.get("phone"),
            "lead_status": lead_data.get("status", "New"),
            "meta_lead_id": lead_data.get("id"),
            "meta_ad_id": lead_data.get("ad_id"),
            "meta_ad_set_id": lead_data.get("adset_id"),
            "meta_campaign_id": lead_data.get("campaign_id"),
            "meta_account_id": lead_data.get("account_id")
        }
        
        if existing:
            # Update existing lead
            doc = creqit.get_doc("Meta Lead", existing[0].name)
            doc.update(lead_doc)
            doc.save()
        else:
            # Create new lead
            doc = creqit.get_doc(lead_doc)
            doc.insert()
            
        return {"status": "success", "lead_id": lead_doc.get("meta_lead_id")}
        
    except Exception as e:
        creqit.log_error("Lead Webhook Error", str(e))
        return {"status": "error", "message": str(e)}
        
def handle_campaign_webhook(data):
    """Handle campaign webhook"""
    # Similar to handle_lead_webhook but for campaigns
    pass
    
def handle_ad_set_webhook(data):
    """Handle ad set webhook"""
    # Similar to handle_lead_webhook but for ad sets
    pass
    
def handle_ad_webhook(data):
    """Handle ad webhook"""
    # Similar to handle_lead_webhook but for ads
    pass 