import creqit
from creqit import _

@creqit.whitelist()
def get_contacts_by_company(contact_name=None, company=None):
    filters = {}
    if contact_name:
        filters['name'] = contact_name
    elif company:
        filters['linkaccount'] = company
    else:
        return []

    contacts = creqit.get_all("Contact_CRM",
        filters=filters,
        fields=["name", "name_surname", "title", "linkaccount", "department", "email", "phone", "mobilephone", "fax", "lastactivity"]
    )
    return contacts
