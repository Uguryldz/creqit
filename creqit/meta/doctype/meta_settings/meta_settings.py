import creqit
from creqit import _
from creqit.model.document import Document
from creqit.utils import now_datetime

class MetaSettings(Document):
    def validate(self):
        if self.sync_enabled and not self.access_token:
            creqit.throw(_("Access Token is required when sync is enabled"))
            
        if self.webhook_enabled and not self.webhook_url:
            creqit.throw(_("Webhook URL is required when webhook is enabled"))
            
        if not hasattr(self, 'sync_enabled'):
            self.sync_enabled = 1
            
    def before_save(self):
        if not self.webhook_secret:
            import secrets
            self.webhook_secret = secrets.token_urlsafe(32)
            
    @staticmethod
    def get_settings():
        """Get Meta settings"""
        settings = creqit.get_doc("Meta Settings")
        if not settings:
            settings = creqit.get_doc({
                "doctype": "Meta Settings",
                "sync_enabled": 1,
                "sync_status": "Not Started"
            })
            settings.insert()
        return settings
        
    def update_sync_status(self, status, error=None):
        """Update sync status"""
        self.sync_status = status
        if status == "Completed":
            self.last_sync_time = now_datetime()
        if error:
            creqit.log_error("Meta Sync Error", error)
        self.save()

    def after_save(self):
        # Clear cache to ensure new settings are reflected
        creqit.cache().delete_value("meta_settings")
        
    @staticmethod
    def get_settings():
        settings = creqit.cache().get_value("meta_settings")
        if not settings:
            settings = creqit.get_doc("Meta Settings", "Meta Settings")
            creqit.cache().set_value("meta_settings", settings)
        return settings 