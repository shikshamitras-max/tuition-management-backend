from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import os

def generate_invoice_pdf(invoice, student, institute):
    """
    invoice  : dict
    student  : dict
    institute: dict
    """

    base_dir = os.path.dirname(os.path.dirname(__file__))
    invoices_dir = os.path.join(base_dir, "invoices")

    if not os.path.exists(invoices_dir):
        os.makedirs(invoices_dir)

    file_path = os.path.join(
        invoices_dir, f"{invoice['invoice_number']}.pdf"
    )

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 50

    # ---------------- HEADER ----------------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, institute["institute_name"])

    c.setFont("Helvetica", 10)
    c.drawString(50, y - 20, institute["address"])
    c.drawString(50, y - 35, f"Contact: {institute['contact']}")

    # ---------------- INVOICE INFO ----------------
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 50, y, "INVOICE")

    c.setFont("Helvetica", 10)
    c.drawRightString(width - 50, y - 20, f"Invoice No: {invoice['invoice_number']}")
    c.drawRightString(width - 50, y - 35, f"Date: {invoice['invoice_date']}")

    # ---------------- STUDENT DETAILS ----------------
    y -= 90
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Student Details")

    c.setFont("Helvetica", 10)
    c.drawString(50, y - 20, f"Name: {student['name']}")
    c.drawString(50, y - 35, f"Batch: {student.get('batch','')}")

    # ---------------- FEES DETAILS ----------------
    y -= 80
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Fees Details")

    c.setFont("Helvetica", 10)
    c.drawString(50, y - 25, f"Total Fees      : ₹ {invoice['total_fees']}")
    c.drawString(50, y - 40, f"Total Paid      : ₹ {invoice['total_paid']}")
    c.drawString(50, y - 55, f"Balance         : ₹ {invoice['balance']}")
    c.drawString(50, y - 70, f"Payment Mode    : {invoice['payment_mode']}")

    # ---------------- FOOTER ----------------
    y -= 130
    c.line(50, y, width - 50, y)

    c.setFont("Helvetica", 10)
    c.drawString(50, y - 30, "Authorized Signature")
    c.drawRightString(width - 50, y - 30, institute["signature_name"])

    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(
        width / 2, 40, "This is a system generated invoice"
    )

    c.showPage()
    c.save()

    return file_path