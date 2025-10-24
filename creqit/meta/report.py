import creqit
from creqit import _
from creqit.meta.meta_client import MetaClient
from creqit.utils import now_datetime, add_days, get_date_str

def get_campaign_performance(campaign_id=None, start_date=None, end_date=None):
    """Get performance metrics for campaigns"""
    client = MetaClient()
    
    if not start_date:
        start_date = get_date_str(add_days(now_datetime(), -30))
    if not end_date:
        end_date = get_date_str(now_datetime())
        
    params = {
        "fields": "campaign_id,campaign_name,impressions,clicks,spend,reach,frequency,ctr,cpc",
        "time_range": {
            "since": start_date,
            "until": end_date
        },
        "time_increment": 1  # Daily breakdown
    }
    
    if campaign_id:
        params["campaign_id"] = campaign_id
        
    return client._make_request("me/insights", params=params)
    
def get_ad_set_performance(ad_set_id=None, start_date=None, end_date=None):
    """Get performance metrics for ad sets"""
    client = MetaClient()
    
    if not start_date:
        start_date = get_date_str(add_days(now_datetime(), -30))
    if not end_date:
        end_date = get_date_str(now_datetime())
        
    params = {
        "fields": "adset_id,adset_name,impressions,clicks,spend,reach,frequency,ctr,cpc",
        "time_range": {
            "since": start_date,
            "until": end_date
        },
        "time_increment": 1  # Daily breakdown
    }
    
    if ad_set_id:
        params["adset_id"] = ad_set_id
        
    return client._make_request("me/insights", params=params)
    
def get_ad_performance(ad_id=None, start_date=None, end_date=None):
    """Get performance metrics for ads"""
    client = MetaClient()
    
    if not start_date:
        start_date = get_date_str(add_days(now_datetime(), -30))
    if not end_date:
        end_date = get_date_str(now_datetime())
        
    params = {
        "fields": "ad_id,ad_name,impressions,clicks,spend,reach,frequency,ctr,cpc",
        "time_range": {
            "since": start_date,
            "until": end_date
        },
        "time_increment": 1  # Daily breakdown
    }
    
    if ad_id:
        params["ad_id"] = ad_id
        
    return client._make_request("me/insights", params=params)
    
def get_lead_performance(campaign_id=None, ad_set_id=None, ad_id=None, start_date=None, end_date=None):
    """Get lead performance metrics"""
    client = MetaClient()
    
    if not start_date:
        start_date = get_date_str(add_days(now_datetime(), -30))
    if not end_date:
        end_date = get_date_str(now_datetime())
        
    params = {
        "fields": "campaign_id,adset_id,ad_id,leads,lead_cost,lead_cost_per_result",
        "time_range": {
            "since": start_date,
            "until": end_date
        },
        "time_increment": 1  # Daily breakdown
    }
    
    if campaign_id:
        params["campaign_id"] = campaign_id
    if ad_set_id:
        params["adset_id"] = ad_set_id
    if ad_id:
        params["ad_id"] = ad_id
        
    return client._make_request("me/insights", params=params)
    
def generate_performance_report(campaign_id=None, start_date=None, end_date=None):
    """Generate a comprehensive performance report"""
    # Get campaign performance
    campaign_insights = get_campaign_performance(campaign_id, start_date, end_date)
    
    # Get ad set performance
    ad_set_insights = get_ad_set_performance(None, start_date, end_date)
    
    # Get ad performance
    ad_insights = get_ad_performance(None, start_date, end_date)
    
    # Get lead performance
    lead_insights = get_lead_performance(campaign_id, None, None, start_date, end_date)
    
    # Combine all insights
    report = {
        "campaigns": campaign_insights.get("data", []),
        "ad_sets": ad_set_insights.get("data", []),
        "ads": ad_insights.get("data", []),
        "leads": lead_insights.get("data", []),
        "period": {
            "start": start_date,
            "end": end_date
        }
    }
    
    return report
    
def save_performance_report(report, report_name=None):
    """Save performance report to a file"""
    if not report_name:
        report_name = f"meta_performance_report_{get_date_str(now_datetime())}.json"
        
    # Create reports directory if it doesn't exist
    reports_dir = creqit.get_site_path("private", "files", "meta_reports")
    creqit.create_folder(reports_dir, exist_ok=True)
    
    # Save report to file
    report_path = creqit.get_site_path("private", "files", "meta_reports", report_name)
    with open(report_path, "w") as f:
        import json
        json.dump(report, f, indent=2)
        
    return report_path 