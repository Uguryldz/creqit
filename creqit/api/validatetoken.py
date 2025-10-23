from creqit.utils import now_datetime
import pytz
import creqit
@creqit.whitelist(allow_guest=True)
def validate_token(token, user):
    try:
        record = creqit.get_all(
            "IntegrationToken",
            filters={"token": token, "user": user},
            fields=["name", "expiry_date"]
        )

        if not record or len(record) > 1:
            return {"status": "notok", "message": "Invalid token or user"}

        record = record[0]

        # UTC -> Yerel zaman dilimi
        local_tz = pytz.timezone("Europe/Istanbul")
        current_time = now_datetime().astimezone(local_tz)
        expiry_date = record["expiry_date"].astimezone(local_tz)

        if current_time > expiry_date:
            return {"status": "notok", "message": "Token expired"}

        return {"status": "ok", "message": "Token is valid"}

    except Exception as e:
        creqit.log_error(creqit.get_traceback(), "Token Validation Error")
        return {"status": "error", "message": str(e)}
