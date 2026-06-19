import os
import qrcode
from io import BytesIO
from typing import Optional
from PIL import Image


def generate_qr_code(data, output_path=None, size=300, border=2, fill_color="#000000", back_color="#FFFFFF"):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(buffer.getvalue())
        buffer.seek(0)
    return buffer


def generate_activity_qr(activity_id, base_url, output_dir="backend/app/static/qrcodes/activities"):
    data = f"{base_url}/activities/{activity_id}/checkin"
    filename = f"activity_{activity_id}.png"
    output_path = os.path.join(output_dir, filename)
    generate_qr_code(data, output_path=output_path)
    return f"/static/qrcodes/activities/{filename}"


def generate_certificate_qr(certificate_number, base_url, output_dir="backend/app/static/qrcodes/certificates"):
    data = f"{base_url}/certificates/verify/{certificate_number}"
    filename = f"cert_{certificate_number}.png"
    output_path = os.path.join(output_dir, filename)
    generate_qr_code(data, output_path=output_path)
    return f"/static/qrcodes/certificates/{filename}"
