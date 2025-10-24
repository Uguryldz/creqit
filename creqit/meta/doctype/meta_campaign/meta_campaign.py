import creqit
from creqit.model.document import Document

class MetaCampaign(Document):
    def before_save(self):
        if not self.meta_campaign_id and self.campaign_id:
            self.meta_campaign_id = self.campaign_id
            
    def validate(self):
        if not self.campaign_objective:
            creqit.throw("Campaign objective is required")
            
    def on_trash(self):
        # Check if there are any ad sets linked to this campaign
        ad_sets = creqit.get_all("Meta Ad Set", filters={"campaign": self.name})
        if ad_sets:
            creqit.throw("Cannot delete campaign with linked ad sets") 