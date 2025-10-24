import creqit
from creqit.model.document import Document

class MetaLead(Document):
    def before_save(self):
        if not self.meta_lead_id and self.lead_id:
            self.meta_lead_id = self.lead_id
            
    def after_insert(self):
        if self.campaign:
            campaign = creqit.get_doc("Meta Campaign", self.campaign)
            if campaign.meta_campaign_id:
                self.meta_campaign_id = campaign.meta_campaign_id
                
        if self.ad_set:
            ad_set = creqit.get_doc("Meta Ad Set", self.ad_set)
            if ad_set.meta_ad_set_id:
                self.meta_ad_set_id = ad_set.meta_ad_set_id
                
        if self.ad:
            ad = creqit.get_doc("Meta Ad", self.ad)
            if ad.meta_ad_id:
                self.meta_ad_id = ad.meta_ad_id
                
        self.save()
        
    def validate(self):
        if not self.lead_email and not self.lead_phone:
            creqit.throw("Either email or phone number is required") 