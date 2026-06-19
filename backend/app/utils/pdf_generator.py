import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime


def _register_fonts():
    try:
        font_path = "/System/Library/Fonts/PingFang.ttc"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("PingFang", font_path))
            return "PingFang"
    except Exception:
        pass
    return "Helvetica"


def generate_certificate_pdf(
    certificate_number: str,
    user_name: str,
    activity_title: str,
    service_hours: float,
    issue_date: datetime = None,
    qr_code_path: str = None,
) -> BytesIO:
    if issue_date is None:
        issue_date = datetime.utcnow()
    buffer = BytesIO()
    font_name = _register_fonts()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CertificateTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=28,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=1 * cm,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "CertificateSubtitle",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=16,
        textColor=colors.HexColor("#7f8c8d"),
        spaceAfter=1.5 * cm,
        alignment=TA_CENTER,
    )
    content_style = ParagraphStyle(
        "CertificateContent",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=14,
        textColor=colors.HexColor("#34495e"),
        spaceAfter=0.8 * cm,
        alignment=TA_CENTER,
        leading=24,
    )
    name_style = ParagraphStyle(
        "CertificateName",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=24,
        textColor=colors.HexColor("#2980b9"),
        spaceAfter=0.8 * cm,
        alignment=TA_CENTER,
    )
    footer_style = ParagraphStyle(
        "CertificateFooter",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor("#95a5a6"),
        alignment=TA_CENTER,
    )
    story = []
    story.append(Paragraph("志愿服务证书", title_style))
    story.append(Paragraph("CERTIFICATE OF VOLUNTEER SERVICE", subtitle_style))
    story.append(Spacer(1, 0.5 * cm))
    border_color = colors.HexColor("#3498db")
    border_table = Table(
        [[""]],
        colWidths=[17 * cm],
        rowHeights=[1 * cm],
    )
    border_table.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (0, 0), (-1, 0), 2, border_color),
                ("LINEBELOW", (0, 0), (-1, 0), 2, border_color),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(border_table)
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("兹证明", content_style))
    story.append(Paragraph(user_name, name_style))
    story.append(Spacer(1, 0.5 * cm))
    content_parts = [
        f"参加了《{activity_title}》志愿服务活动，",
        f"累计服务时长 {service_hours} 小时。",
    ]
    for part in content_parts:
        story.append(Paragraph(part, content_style))
    story.append(Spacer(1, 1 * cm))
    date_str = issue_date.strftime("%Y年%m月%d日")
    story.append(Paragraph(f"颁发日期：{date_str}", content_style))
    story.append(Paragraph(f"证书编号：{certificate_number}", content_style))
    story.append(Spacer(1, 1 * cm))
    if qr_code_path and os.path.exists(qr_code_path):
        qr_img = Image(qr_code_path, width=3 * cm, height=3 * cm)
        qr_table = Table([[qr_img]], colWidths=[3 * cm])
        qr_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        story.append(qr_table)
        story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("本证书由志愿服务平台自动生成，可通过证书编号在平台验证。", footer_style))
    doc.build(story)
    buffer.seek(0)
    return buffer
