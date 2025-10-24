import creqit
from creqit.model.document import Document

class MetaCountry(Document):
    def validate(self):
        if not self.country_code or not self.country_name:
            creqit.throw("Country code and name are required")
            
        # Check for duplicate country codes
        existing = creqit.get_all("Meta Country", filters={
            "country_code": self.country_code,
            "name": ["!=", self.name]
        })
        if existing:
            creqit.throw(f"Country code {self.country_code} already exists") 