import creqit
from creqit.model.document import Document

class MetaAdSet(Document):
    def before_save(self):
        if not self.meta_ad_set_id and self.ad_set_id:
            self.meta_ad_set_id = self.ad_set_id
            
    def after_insert(self):
        if self.campaign:
            campaign = creqit.get_doc("Meta Campaign", self.campaign)
            if campaign.meta_campaign_id:
                self.meta_campaign_id = campaign.meta_campaign_id
                self.meta_account_id = campaign.meta_account_id
                self.save()
                
    def validate(self):
        if self.targeting_age_min > self.targeting_age_max:
            creqit.throw("Minimum age cannot be greater than maximum age")
            
        if not self.targeting_countries:
            creqit.throw("At least one targeting country is required") 