from flask import Blueprint, send_file
from database.db import get_db_connection
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date
import os

weekly_pdf_bp = Blueprint("weekly_pdf_bp", __name__)

@weekly_pdf_bp.route("/report-card/weekly/<int:student_id>/<exam_name>", methods=["GET"])
def weekly_report_pdf(student_id, exam_name):
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
        SELECT subject, total_marks, obtained_marks,
               ROUND((obtained_marks * 100.0) / total_marks, 2) AS percentage
        FROM results
        WHERE student_id = ?
        AND exam_name = ?
    """, (student_id, exam_name))

    results = cursor.fetchall()
    conn.close()

    if not student or not results:
        return {"error": "No data found"}, 404

    os.makedirs("static", exist_ok=True)
    file_path = f"static/weekly_report_{student_id}_{exam_name}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # -------- LOGO --------
    logo_path = institute["logo_path"]
    if logo_path and os.path.exists(logo_path):
        c.drawImage(
            logo_path,
            40,
            height - 90,
            width=60,
            height=60,
            preserveAspectRatio=True
        )

    # -------- HEADER --------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(120, height - 50, institute["name"])

    c.setFont("Helvetica", 10)
    c.drawString(120, height - 70, institute["address"])
    c.drawString(120, height - 85, f"Phone: {institute['phone']}")

    # -------- REPORT INFO --------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 130, "WEEKLY EXAM REPORT")

    c.setFont("Helvetica", 10)
    c.drawString(40, height - 150, f"Student Name: {student['name']}")
    c.drawString(40, height - 165, f"Class: {student['batch']}")
    c.drawString(40, height - 180, f"Exam: {exam_name}")
    c.drawString(40, height - 195, f"Date: {date.today()}")

    # -------- TABLE --------
    y = height - 230
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Subject")
    c.drawString(220, y, "Total")
    c.drawString(280, y, "Obtained")
    c.drawString(360, y, "%")

    c.setFont("Helvetica", 10)
    for r in results:
        y -= 20
        c.drawString(40, y, r["subject"])
        c.drawString(220, y, str(r["total_marks"]))
        c.drawString(280, y, str(r["obtained_marks"]))
        c.drawString(360, y, str(r["percentage"]))

    # -------- SIGNATURE --------
    y -= 50
    c.drawString(40, y, "Authorized Signature")
    c.drawString(40, y - 15, institute["signature_name"])

    c.showPage()
    c.save()

    return send_file(file_path, as_attachment=True)