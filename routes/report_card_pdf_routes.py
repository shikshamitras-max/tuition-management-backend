from flask import Blueprint, send_file
from database.db import get_db_connection
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date
import os

report_pdf_bp = Blueprint("report_pdf_bp", __name__)

@report_pdf_bp.route("/report-card/pdf/<int:student_id>", methods=["GET"])
def report_card_pdf(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # -------- Institute --------
    cursor.execute("SELECT * FROM institute WHERE id = 1")
    institute = cursor.fetchone()

    # -------- Student --------
    cursor.execute("SELECT name, batch FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()

    # -------- Results --------
    cursor.execute("""
        SELECT
            exam_name,
            subject,
            total_marks,
            obtained_marks,
            ROUND((obtained_marks * 100.0) / total_marks, 2) AS percentage
        FROM results
        WHERE student_id = ?
        ORDER BY exam_date, subject
    """, (student_id,))
    results = cursor.fetchall()

    conn.close()

    if not student or not results:
        return {"error": "No report data found"}, 404

    total_marks = sum(r["total_marks"] for r in results)
    obtained_marks = sum(r["obtained_marks"] for r in results)
    percentage = round((obtained_marks * 100) / total_marks, 2)

    if percentage >= 85:
        remark = "Excellent"
    elif percentage >= 60:
        remark = "Good"
    else:
        remark = "Needs Improvement"

    # -------- Create PDF --------
    os.makedirs("static", exist_ok=True)
    file_path = f"static/report_card_student_{student_id}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # -------- Logo --------
    if institute["logo_path"] and os.path.exists(institute["logo_path"]):
        c.drawImage(institute["logo_path"], 40, height - 100, width=70, height=70)

    # -------- Header --------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(130, height - 50, institute["name"])

    c.setFont("Helvetica", 10)
    c.drawString(130, height - 70, institute["address"])
    c.drawString(130, height - 85, f"Phone: {institute['phone']}")

    # -------- Title --------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 130, "STUDENT REPORT CARD")

    # -------- Student Info --------
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 155, f"Student Name: {student['name']}")
    c.drawString(300, height - 155, f"Class: {student['batch']}")
    c.drawString(40, height - 170, f"Report Date: {date.today()}")

    # -------- Table Header --------
    y = height - 210
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "S.No")
    c.drawString(80, y, "Exam")
    c.drawString(180, y, "Subject")
    c.drawString(300, y, "Total")
    c.drawString(350, y, "Obtained")
    c.drawString(430, y, "%")

    c.line(40, y - 2, width - 40, y - 2)

    # -------- Table Rows --------
    c.setFont("Helvetica", 10)
    for i, r in enumerate(results, start=1):
        y -= 20
        c.drawString(40, y, str(i))
        c.drawString(80, y, r["exam_name"])
        c.drawString(180, y, r["subject"])
        c.drawString(300, y, str(r["total_marks"]))
        c.drawString(350, y, str(r["obtained_marks"]))
        c.drawString(430, y, str(r["percentage"]))

    # -------- Summary --------
    y -= 40
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Overall Performance")

    c.setFont("Helvetica", 10)
    y -= 15
    c.drawString(40, y, f"Total Marks: {total_marks}")
    y -= 15
    c.drawString(40, y, f"Obtained Marks: {obtained_marks}")
    y -= 15
    c.drawString(40, y, f"Percentage: {percentage}%")
    y -= 15
    c.drawString(40, y, f"Remark: {remark}")

    # -------- Signature --------
    y -= 50
    c.drawString(40, y, "Authorized Signature")
    c.drawString(40, y - 15, institute["signature_name"])

    c.showPage()
    c.save()

    return send_file(file_path, as_attachment=True)