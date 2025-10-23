import creqit
from creqit import _
from datetime import date

@creqit.whitelist(allow_guest=True)
def check_license(license_number, app_number):
    today = date.today()

    customer = creqit.get_all("Customer", 
        filters={
            "license_number": license_number,
            "app_number": app_number,
            "is_active": 1,
            "start_date": ["<=", today],
            "end_date": [">=", today]
        },
        fields=["name", "customer_name", "max_user_count", "start_date", "end_date"]
    )

    if not customer:
        return {
            "valid": False,
            "message": "Geçerli bir lisans bulunamadı ya da lisans süresi geçmiş."
        }

    customer_name = customer[0].name
    max_users = customer[0].max_user_count or 0

    # Aktif modülleri bul
    customer_modules = creqit.get_all("CustomerModule",
        filters={
            "customer": customer_name,
            "isactive": 1,
            "start_date": ["<=", today],
            "end_date": [">=", today]
        },
        fields=["module"]
    )

    module_names = [cm.module for cm in customer_modules]

    # Modül detaylarını çek
    modules = creqit.get_all("Modules",
        filters={
            "name": ["in", module_names],
            "isactive": 1,
            "start_date": ["<=", today],
            "end_date": [">=", today]
        },
        fields=["module_code", "end_date"]
    )

    expires_at = str(max([m.end_date for m in modules])) if modules else None

    return {
        "valid": True,
        "message": "Lisans geçerli.",
        "license_info": {
            "expires_at": expires_at,
            "max_users": max_users,
            "modules": [m.module_code for m in modules]
        }
    }
