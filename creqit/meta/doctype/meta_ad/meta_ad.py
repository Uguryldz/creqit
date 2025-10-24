import creqit
from creqit.model.document import Document

class MetaAd(Document):
    def before_save(self):
        if not self.meta_ad_id and self.ad_id:
            self.meta_ad_id = self.ad_id
            
    def after_insert(self):
        if self.ad_set:
            ad_set = creqit.get_doc("Meta Ad Set", self.ad_set)
            if ad_set.meta_ad_set_id:
                self.meta_ad_set_id = ad_set.meta_ad_set_id
                self.meta_campaign_id = ad_set.meta_campaign_id
                self.meta_account_id = ad_set.meta_account_id
                self.save()
                
    def validate(self):
        if self.creative_type == "Image" and not self.creative_image_url:
            creqit.throw("Creative Image URL is required for Image type ads")
        elif self.creative_type == "Video" and not self.creative_video_url:
            creqit.throw("Creative Video URL is required for Video type ads") 