from flask import Blueprint, send_file
from database.db import get_db_connection
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date
import os

performance_graph_bp = Blueprint("performance_graph_bp", __name__)

@performance_graph_bp.route("/report-card/graph/<int:student_id>", methods=["GET"])
def performance_graph_pdf(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # -------- Institute --------
    cursor.execute("SELECT * FROM institute WHERE id = 1")
    institute = cursor.fetchone()

    # -------- Student --------
    cursor.execute("SELECT name, batch FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()

    # -------- Subject Performance --------
    cursor.execute("""
        SELECT
            subject,
            ROUND((SUM(obtained_marks) * 100.0) / SUM(total_marks), 2) AS percentage
        FROM results
        WHERE student_id = ?
        GROUP BY subject
    """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    if not student or not rows:
        return {"error": "No performance data"}, 404

    subjects = [r["subject"] for r in rows]
    percentages = [r["percentage"] for r in rows]

    os.makedirs("static", exist_ok=True)

    # -------- CREATE GRAPH IMAGE --------
    graph_path = f"static/graph_{student_id}.png"

    plt.figure(figsize=(6, 4))
    plt.bar(subjects, percentages)
    plt.ylim(0, 100)
    plt.ylabel("Percentage")
    plt.title("Subject-wise Performance")
    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close()

    # -------- CREATE PDF --------
    pdf_path = f"static/performance_graph_{student_id}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Logo
    if institute["logo_path"] and os.path.exists(institute["logo_path"]):
        c.drawImage(institute["logo_path"], 40, height - 90, width=60, height=60)

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(120, height - 50, institute["name"])

    c.setFont("Helvetica", 10)
    c.drawString(120, height - 70, institute["address"])
    c.drawString(120, height - 85, f"Phone: {institute['phone']}")

    # Title
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 130, "STUDENT PERFORMANCE GRAPH")

    c.setFont("Helvetica", 10)
    c.drawString(40, height - 150, f"Student Name: {student['name']}")
    c.drawString(40, height - 165, f"Class: {student['batch']}")
    c.drawString(40, height - 180, f"Date: {date.today()}")

    # Graph
    c.drawImage(graph_path, 60, height - 520, width=480, height=300)

    # Signature
    c.drawString(40, 100, "Authorized Signature")
    c.drawString(40, 85, institute["signature_name"])

    c.showPage()
    c.save()

    return send_file(pdf_path, as_attachment=True)