import creqit
from creqit import _
from creqit.meta.sync import sync_all
from creqit.meta.doctype.meta_settings.meta_settings import MetaSettings

def sync_meta_data():
    """Background job to sync Meta data"""
    try:
        settings = MetaSettings.get_settings()
        if settings.sync_enabled:
            sync_all()
    except Exception as e:
        creqit.log_error("Meta Scheduler Error", str(e))

def setup_scheduler():
    """Setup scheduler for Meta sync"""
    settings = MetaSettings.get_settings()
    if settings.sync_enabled:
        # Remove existing job if any
        creqit.delete_doc("Scheduled Job Type", "Meta Sync", ignore_permissions=True)
        
        # Create new job
        job = creqit.get_doc({
            "doctype": "Scheduled Job Type",
            "method": "creqit.meta.scheduler.sync_meta_data",
            "frequency": settings.sync_interval,
            "cron_format": f"*/{settings.sync_interval//60} * * * *",
            "status": "Active"
        })
        job.insert(ignore_permissions=True) 