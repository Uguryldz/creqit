import jwt

from datetime import timedelta
from creqit.utils import now_datetime
import creqit

SECRET_KEY = "20122910"

@creqit.whitelist(allow_guest=True)
def generate_token():
    user_id = creqit.local.session.user
    exp = now_datetime() + timedelta(minutes=15)
    
    if SECRET_KEY == '20122910':  # Doğru bir if-else yapısı
        payload = {
            "user_id": user_id,
            "exp": exp
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
        save_token_to_doctype(user_id, token, exp)  # Token kaydetme
        return {"token": token, "userid": user_id,"exp": exp}
    else:
        return {"error": "Secret Key is not allowed"}

def save_token_to_doctype(user_id, token, expiry):
    creqit.get_doc({
        "doctype": "IntegrationToken",
        "token": token,
        "user": user_id,
        "expiry_date": expiry
    }).insert(ignore_permissions=True)