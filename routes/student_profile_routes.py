from flask import Blueprint, jsonify
from database.db import get_db_connection

profile_bp = Blueprint("profile_bp", __name__)

@profile_bp.route("/student/profile/<int:student_id>", methods=["GET"])
def student_profile(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ---------------- STUDENT BASIC INFO ----------------
    cursor.execute("""
        SELECT id, name, phone, batch, fees_paid, total_fees
        FROM students
        WHERE id = ?
    """, (student_id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    # ---------------- ATTENDANCE ----------------
    cursor.execute("""
        SELECT
            COUNT(*) AS total_days,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_days
        FROM attendance
        WHERE student_id = ?
    """, (student_id,))
    att = cursor.fetchone()

    total_days = att["total_days"] or 0
    present_days = att["present_days"] or 0
    attendance_percent = round((present_days / total_days) * 100, 2) if total_days else 0

    # ---------------- EXAMS ----------------
    cursor.execute("""
        SELECT
            exam_name,
            subject,
            total_marks,
            obtained_marks,
            ROUND((obtained_marks * 100.0) / total_marks, 2) AS percentage,
            exam_date
        FROM results
        WHERE student_id = ?
        ORDER BY exam_date
    """, (student_id,))
    exams = [dict(row) for row in cursor.fetchall()]

    # ---------------- GROWTH (SUBJECT-WISE) ----------------
    cursor.execute("""
        SELECT subject, exam_date,
               ROUND((obtained_marks * 100.0) / total_marks, 2) AS percentage
        FROM results
        WHERE student_id = ?
        ORDER BY subject, exam_date
    """, (student_id,))
    rows = cursor.fetchall()

    growth = {}
    previous = {}

    for row in rows:
        subject = row["subject"]
        percent = row["percentage"]

        change = None
        if subject in previous:
            change = round(percent - previous[subject], 2)

        previous[subject] = percent

        growth.setdefault(subject, []).append({
            "exam_date": row["exam_date"],
            "percentage": percent,
            "change": change
        })

    conn.close()

    return jsonify({
        "student": {
            "id": student["id"],
            "name": student["name"],
            "phone": student["phone"],
            "batch": student["batch"]
        },
        "attendance": {
            "total_days": total_days,
            "present_days": present_days,
            "percentage": attendance_percent
        },
        "fees": {
            "total_fees": student["total_fees"],
            "total_paid": student["fees_paid"],
            "outstanding": student["total_fees"] - student["fees_paid"]
        },
        "exams": exams,
        "growth": growth
    })