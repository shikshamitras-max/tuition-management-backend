from flask import Blueprint, send_file
from database.db import get_db_connection
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date
import os

monthly_pdf_bp = Blueprint("monthly_pdf_bp", __name__)

@monthly_pdf_bp.route("/report-card/monthly/<int:student_id>/<int:year>/<int:month>", methods=["GET"])
def monthly_report_pdf(student_id, year, month):
    conn = get_db_connection()
    cursor = conn.cursor()

    # -------- Institute --------
    cursor.execute("SELECT * FROM institute WHERE id = 1")
    institute = cursor.fetchone()

    # -------- Student --------
    cursor.execute("SELECT name, batch FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()

    # -------- Monthly Results --------
    cursor.execute("""
        SELECT
            subject,
            SUM(total_marks) AS total_marks,
            SUM(obtained_marks) AS obtained_marks,
            ROUND((SUM(obtained_marks) * 100.0) / SUM(total_marks), 2) AS percentage
        FROM results
        WHERE student_id = ?
        AND strftime('%Y', exam_date) = ?
        AND strftime('%m', exam_date) = ?
        GROUP BY subject
    """, (student_id, str(year), f"{month:02d}"))

    results = cursor.fetchall()
    conn.close()

    if not student or not results:
        return {"error": "No monthly data found"}, 404

    os.makedirs("static", exist_ok=True)
    file_path = f"static/monthly_report_{student_id}_{year}_{month}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # -------- LOGO --------
    if institute["logo_path"] and os.path.exists(institute["logo_path"]):
        c.drawImage(
            institute["logo_path"],
            40, height - 90,
            width=60, height=60,
            preserveAspectRatio=True
        )

    # -------- HEADER --------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(120, height - 50, institute["name"])

    c.setFont("Helvetica", 10)
    c.drawString(120, height - 70, institute["address"])
    c.drawString(120, height - 85, f"Phone: {institute['phone']}")

    # -------- TITLE --------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 130, "MONTHLY PERFORMANCE REPORT")

    c.setFont("Helvetica", 10)
    c.drawString(40, height - 150, f"Student Name: {student['name']}")
    c.drawString(40, height - 165, f"Class: {student['batch']}")
    c.drawString(40, height - 180, f"Month: {month}/{year}")
    c.drawString(40, height - 195, f"Generated On: {date.today()}")

    # -------- TABLE --------
    y = height - 230
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Subject")
    c.drawString(220, y, "Total")
    c.drawString(280, y, "Obtained")
    c.drawString(360, y, "%")

    total_marks = 0
    obtained_marks = 0

    c.setFont("Helvetica", 10)
    for r in results:
        y -= 20
        c.drawString(40, y, r["subject"])
        c.drawString(220, y, str(r["total_marks"]))
        c.drawString(280, y, str(r["obtained_marks"]))
        c.drawString(360, y, str(r["percentage"]))

        total_marks += r["total_marks"]
        obtained_marks += r["obtained_marks"]

    percentage = round((obtained_marks * 100) / total_marks, 2)

    remark = (
        "Excellent" if percentage >= 85 else
        "Good" if percentage >= 60 else
        "Needs Improvement"
    )

    # -------- SUMMARY --------
    y -= 40
    c.drawString(40, y, f"Total Marks: {total_marks}")
    y -= 15
    c.drawString(40, y, f"Obtained Marks: {obtained_marks}")
    y -= 15
    c.drawString(40, y, f"Overall Percentage: {percentage}%")
    y -= 15
    c.drawString(40, y, f"Remark: {remark}")

    # -------- SIGNATURE --------
    y -= 50
    c.drawString(40, y, "Authorized Signature")
    c.drawString(40, y - 15, institute["signature_name"])

    c.showPage()
    c.save()

    return send_file(file_path, as_attachment=True)