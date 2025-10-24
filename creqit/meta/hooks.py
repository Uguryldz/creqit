import creqit
from creqit import _
from creqit.meta.scheduler import setup_scheduler

def after_install():
    """After install hook"""
    setup_scheduler()
    
def after_uninstall():
    """After uninstall hook"""
    # Clean up scheduled jobs
    creqit.delete_doc("Scheduled Job Type", "Meta Sync", ignore_permissions=True)
    
    # Clear cache
    creqit.cache().delete_value("meta_settings")
    
def on_session_creation():
    """On session creation hook"""
    # Initialize Meta settings if not exists
    from creqit.meta.doctype.meta_settings.meta_settings import MetaSettings
    MetaSettings.get_settings()
    
def on_update():
    """On update hook"""
    setup_scheduler() 