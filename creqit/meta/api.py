import creqit
from creqit import _
from creqit.api import build_response
from creqit.meta.webhook import handle_webhook
from creqit.meta.report import generate_performance_report, save_performance_report
from creqit.meta.sync import sync_all
from creqit.meta.doctype.meta_settings.meta_settings import MetaSettings

@creqit.whitelist(allow_guest=True)
def webhook():
    """Handle incoming webhook from Meta"""
    try:
        request_data = creqit.request.get_json()
        result = handle_webhook(request_data)
        return build_response({"message": "Webhook processed", "result": result})
    except Exception as e:
        creqit.log_error(f"Webhook Error: {str(e)}")
        return {"error": True, "message": "Webhook processing failed", "error_details": str(e)}
        
@creqit.whitelist()
def sync():
    """Manually trigger sync"""
    try:
        sync_all()
        return build_response({"message": "Sync completed successfully"})
    except Exception as e:
        creqit.log_error(f"Sync Error: {str(e)}")
        return {"error": True, "message": "Sync failed", "error_details": str(e)}
        
@creqit.whitelist()
def generate_report(campaign_id=None, start_date=None, end_date=None):
    """Generate performance report"""
    try:
        report = generate_performance_report(campaign_id, start_date, end_date)
        report_path = save_performance_report(report)
        return build_response({
            "message": "Report generated successfully",
            "report_path": report_path
        })
    except Exception as e:
        creqit.log_error(f"Report Generation Error: {str(e)}")
        return {"error": True, "message": "Report generation failed", "error_details": str(e)}
        
@creqit.whitelist()
def get_settings():
    """Get Meta settings"""
    try:
        settings = MetaSettings.get_settings()
        return build_response({
            "sync_enabled": settings.sync_enabled,
            "sync_interval": settings.sync_interval,
            "last_sync": settings.last_sync,
            "sync_status": settings.sync_status,
            "webhook_enabled": settings.webhook_enabled,
            "webhook_url": settings.webhook_url
        })
    except Exception as e:
        creqit.log_error(f"Settings Error: {str(e)}")
        return {"error": True, "message": "Failed to get settings", "error_details": str(e)}
        
@creqit.whitelist()
def update_settings(**kwargs):
    """Update Meta settings"""
    try:
        settings = MetaSettings.get_settings()
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        settings.save()
        return build_response({"message": "Settings updated successfully"})
    except Exception as e:
        creqit.log_error(f"Settings Update Error: {str(e)}")
        return {"error": True, "message": "Failed to update settings", "error_details": str(e)}
        
@creqit.whitelist()
def get_stats():
    """Get Meta statistics"""
    try:
        stats = {
            "campaigns": creqit.db.count("Meta Campaign"),
            "ad_sets": creqit.db.count("Meta Ad Set"),
            "ads": creqit.db.count("Meta Ad"),
            "leads": creqit.db.count("Meta Lead")
        }
        return build_response(stats)
    except Exception as e:
        creqit.log_error(f"Stats Error: {str(e)}")
        return {"error": True, "message": "Failed to get stats", "error_details": str(e)} 