import uuid
from datetime import datetime
from typing import Optional


def generate_certificate_number(prefix="VOL", user_id=None, activity_id=None):
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    random_part = str(uuid.uuid4().hex)[:8].upper()
    parts = [prefix, date_str]
    if user_id:
        parts.append(f"U{user_id:06d}")
    if activity_id:
        parts.append(f"A{activity_id:06d}")
    parts.append(random_part)
    return "-".join(parts)


def generate_certificate_filename(certificate_number, user_name):
    clean_name = "".join(c for c in user_name if c.isalnum() or c in (" ", "-", "_")).strip()
    clean_name = clean_name.replace(" ", "_")
    return f"{certificate_number}_{clean_name}.pdf"


def generate_verification_url(certificate_number, base_url="http://localhost:8000"):
    return f"{base_url}/api/v1/certificates/verify/{certificate_number}"
