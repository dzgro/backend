from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from datetime import datetime
import requests
from io import BytesIO
from num2words import num2words
from math import cos, sin, pi
import io, boto3
from dzgroshared.models.collections.user import User

def draw_stamp(c, center_x, center_y, radius):
    # --- Outer Circle ---
    c.setStrokeColorRGB(0.2, 0.2, 0.8)
    c.setLineWidth(2)
    c.circle(center_x, center_y, radius)

    # --- Inner Circle ---
    inner_radius = radius - 12
    c.setLineWidth(1)
    c.circle(center_x, center_y, inner_radius)

    # --- Center Text: Jaipur ---
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0.2, 0.2, 0.8)
    c.drawCentredString(center_x, center_y - 4, "Jaipur")

    # --- Arc Text Drawer ---
    def draw_arc_text(text, cx, cy, r, start_at_top=True, angle_per_char_deg=12):
        total_chars = len(text)
        total_arc = angle_per_char_deg * (total_chars - 1)

        if start_at_top:
            center_angle_deg = 90 + total_arc / 2  # shift so first letter starts at top-center
        else:
            center_angle_deg = 90

        start_angle = center_angle_deg - total_arc

        for i, char in enumerate(text):
            angle_deg = start_angle + i * angle_per_char_deg
            angle_rad = pi * angle_deg / 180
            x = cx + r * cos(angle_rad)
            y = cy + r * sin(angle_rad)

            c.saveState()
            c.translate(x, y)
            c.rotate(angle_deg + 90)  # upright and readable
            c.setFont("Helvetica", 7)
            c.setFillColorRGB(0.2, 0.2, 0.8)
            c.drawString(-2, 0, char)
            c.restoreState()

    # --- Arc Text ---
    arc_text = "DZGRO • TECHNOLOGIES"
    arc_radius = radius - 4  # tight spacing inside outer ring
    draw_arc_text(arc_text, center_x, center_y, arc_radius, start_at_top=True, angle_per_char_deg=12)

def generate_gst_invoice(user: User,
    amount: float, gst_rate: int,
    invoice_number: str, date: datetime
):
    seller_gstin = "08DQAPS9574Q1ZN"
    seller_name = "DZGRO TECHNOLOGIES"
    seller_address1 = "4TH FLOOR, B4-401, Kanchanjunga Apartments"
    seller_address2 = "Sector 8, Indira Gandhi Nagar, Jagatpura"
    seller_address3 = "Jaipur, Rajasthan, 302017"

    gst_amount = round(amount-amount/ (100+gst_rate)*100, 2)
    is_intrastate = user.business.gstin.startswith("08") if user.business else True
    cgst = sgst = igst = 0.0

    if is_intrastate:
        cgst = sgst = round(gst_amount / 2, 2)
    else:
        igst = gst_amount
    total = round(amount, 2)
    amount = round(amount-gst_amount,2)

    # Convert total to words in Indian format
    def amount_in_words(n):
        return num2words(n, lang='en_IN').replace(",", "").title() + " Rupees Only"
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    width, height = A4

    # --- Header: TAX INVOICE ---
    c.setFont("Helvetica-Bold", 16)
    title_y = height - 60
    c.drawCentredString(width / 2, title_y, "TAX INVOICE")
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(30, title_y - 5, width - 30, title_y - 5)

    # --- Invoice No. and Date (just below title, no gap from Bill From) ---
    y = title_y - 25
    c.setFont("Helvetica-Bold", 9)
    c.drawString(30, y, f"Invoice No: {invoice_number}")
    from date_util import DateHelper
    dateString = DateHelper().convertDateToZonalDate(date, 'Asia/Kolkata').strftime('%d-%m-%Y')
    c.drawRightString(width - 30, y, f"Date: {dateString}")

    # --- Logo under title, aligned to top-right ---
    logo_width = 80
    try:
        response = requests.get("https://dzgro.com/assets/logo.png")
        if response.status_code == 200:
            logo = BytesIO(response.content)
            logo_img = ImageReader(logo)
            img_w, img_h = logo_img.getSize()
            aspect = img_h / float(img_w)
            logo_draw_height = logo_width * aspect
            c.drawImage(logo_img, width - 30 - logo_width, y - logo_draw_height - 10,
                        width=logo_width, height=logo_draw_height, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"Logo load error: {e}")

    # --- Seller Info with "Bill From" ---
    y -= 25
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y, "Bill From:")
    c.setFont("Helvetica", 9)
    c.drawString(30, y - 12, f"{seller_name}")
    c.drawString(30, y - 24, f"{seller_address1}")
    c.drawString(30, y - 36, f"{seller_address2}")
    c.drawString(30, y - 48, f"{seller_address3}")
    c.drawString(30, y - 60, f"GSTIN: {seller_gstin}")

    # --- Buyer Info with "Bill To" ---
    y -= 90
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y, "Bill To:")
    c.setFont("Helvetica", 9)
    if user.business:
        c.drawString(30, y - 12, f"{user.business.name}")
        c.drawString(30, y - 24, user.business.addressline1)
        c.drawString(30, y - 36, user.business.addressline2)
        c.drawString(30, y - 48, user.business.addressline3)
        c.drawString(30, y - 60, f'{user.business.city} {user.business.state} - {user.business.pincode}')
        c.drawString(30, y - 72, f"GSTIN: {user.business.gstin}")
    else: c.drawString(30, y - 12, f"{user.name}")
    c.drawString(30, y - 84, f"Place of Supply: Rajasthan")

    # --- Table ---
    y -= 110
    table_x = 30
    table_width = width - 2 * table_x
    row_height = 18
    rows = [["Description", "Amount (INR)"]]
    rows.append(["Subscription Charges", f"{amount:.2f}"])
    if is_intrastate:
        rows.append([f"CGST @ {gst_rate / 2:.1f}%", f"{cgst:.2f}"])
        rows.append([f"SGST @ {gst_rate / 2:.1f}%", f"{sgst:.2f}"])
    else:
        rows.append([f"IGST @ {gst_rate:.1f}%", f"{igst:.2f}"])
    rows.append(["Total Payable", f"{total:.2f}"])

    c.setFont("Helvetica", 9)
    for i, row in enumerate(rows):
        row_y = y - i * row_height
        c.line(table_x, row_y, table_x + table_width, row_y)
        c.drawString(table_x + 5, row_y - 14, row[0])
        c.drawRightString(table_x + table_width - 5, row_y - 14, row[1])
    bottom_y = y - len(rows) * row_height
    c.line(table_x, bottom_y, table_x + table_width, bottom_y)
    c.line(table_x, y, table_x, bottom_y)
    c.line(table_x + table_width * 0.75, y, table_x + table_width * 0.75, bottom_y)
    c.line(table_x + table_width, y, table_x + table_width, bottom_y)

    # --- Amount in Words ---
    y = bottom_y - 20
    c.setFont("Helvetica-Bold", 9)
    c.drawString(30, y, "Amount in Words:")
    c.setFont("Helvetica", 9)
    c.drawString(110, y, amount_in_words(total))

    # --- Terms & Conditions and Authorized Signatory (on same line) ---
    y -= 40
    c.setFont("Helvetica-Bold", 9)
    c.drawString(30, y, "Terms & Conditions:")
    c.drawRightString(width - 30, y, "Authorized Signatory")

    c.setFont("Helvetica", 8)
    terms = [
        "1. This invoice is for Dzgro Software usage.",
        "2. Payment is non-refundable.",
        "3. Legal jurisdiction: Jaipur, Rajasthan."
    ]
    for i, line in enumerate(terms):
        c.drawString(30, y - (15 * (i + 1)), line)

    # Disclaimer under signatory
    disclaimer_y = y - (15 * (len(terms) + 1))
    draw_stamp(c, width - 80, disclaimer_y + 45, 30)

    c.setFont("Helvetica", 7)
    c.setFont("Helvetica-Oblique", 7)
    c.drawRightString(width - 30, disclaimer_y, "This is a system-generated e-invoice and")
    c.drawRightString(width - 30, disclaimer_y - 12, "does not require a physical signature.")
    
    c.save()
    return buffer
    
