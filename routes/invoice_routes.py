from flask import Blueprint, jsonify, send_file
from database.db import get_db_connection
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import date
import os

invoice_bp = Blueprint("invoice_bp", __name__)

def amount_to_words(n):
    ones = ["","One","Two","Three","Four","Five","Six","Seven","Eight","Nine"]
    tens = ["","Ten","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]

    if n < 10:
        return ones[n]
    elif n < 100:
        return tens[n//10] + " " + ones[n%10]
    elif n < 1000:
        return ones[n//100] + " Hundred " + amount_to_words(n%100)
    else:
        return str(n)

@invoice_bp.route("/invoice/<int:student_id>", methods=["GET"])
def generate_invoice(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # -------- Institute --------
    cursor.execute("SELECT * FROM institute WHERE id = 1")
    institute = cursor.fetchone()

    # -------- Student --------
    cursor.execute("SELECT name, batch, fees_paid, total_fees FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return {"error": "Student not found"}, 404

    total_paid = student["fees_paid"]
    total_fees = student["total_fees"]
    outstanding = total_fees - total_paid

    # -------- Create PDF --------
    file_path = os.path.join("static", f"Invoice_Student_{student_id}.pdf")
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

   # Logo (from DB)
    logo_path = institute["logo_path"]
    if logo_path and os.path.exists(logo_path):
        c.drawImage(logo_path, 40, height - 100, width=70, height=70)

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(120, height - 50, institute["name"])

    c.setFont("Helvetica", 10)
    c.drawString(120, height - 70, institute["address"])
    c.drawString(120, height - 85, f"Phone: {institute['phone']}")

    # Invoice Info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 140, "INVOICE")

    c.setFont("Helvetica", 10)
    c.drawString(40, height - 160, f"Date: {date.today().isoformat()}")
    c.drawString(40, height - 175, f"Invoice No: INV-{student_id}-{date.today().year}")

    # Student Info
    c.drawString(40, height - 210, f"Student Name: {student['name']}")
    c.drawString(40, height - 225, f"Batch/Class: {student['batch']}")

    # Fees Table
    y = height - 270
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Description")
    c.drawString(300, y, "Amount")

    c.setFont("Helvetica", 10)
    y -= 20
    c.drawString(40, y, "Total Fees")
    c.drawString(300, y, f"₹ {total_fees}")

    y -= 20
    c.drawString(40, y, "Total Paid")
    c.drawString(300, y, f"₹ {total_paid}")

    y -= 20
    c.drawString(40, y, "Outstanding")
    c.drawString(300, y, f"₹ {outstanding}")

    # Amount in words
    y -= 40
    c.drawString(40, y, f"Amount Paid (in words): {amount_to_words(total_paid)} Rupees Only")

    # Signature
    y -= 80
    c.drawString(40, y, "Authorized Signature")
    if institute["signature_name"]:
        c.drawString(40, y - 15, institute["signature_name"])


    c.showPage()
    c.save()

    # -------- SAVE INVOICE RECORD --------
    cursor.execute("""
    INSERT INTO invoices (
    student_id, invoice_no, invoice_date,
    total_fees, total_paid, outstanding
    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
    student_id,
    f"INV-{student_id}-{date.today().year}",
    date.today().isoformat(),
    total_fees,
    total_paid,
    outstanding
    ))
    conn.commit()

    conn.close()
    return send_file(file_path, as_attachment=True)

@invoice_bp.route("/invoices/<int:student_id>", methods=["GET"])
def invoice_history(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT invoice_no, invoice_date,
               total_fees, total_paid, outstanding
        FROM invoices
        WHERE student_id = ?
        ORDER BY invoice_date DESC
    """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])