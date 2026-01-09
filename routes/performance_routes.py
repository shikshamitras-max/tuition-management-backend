from flask import Blueprint, jsonify
from database.db import get_db_connection

performance_bp = Blueprint("performance_bp", __name__)

@performance_bp.route("/student/performance/<int:student_id>", methods=["GET"])
def student_performance(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ---------- Student ----------
    cursor.execute(
        "SELECT name, batch FROM students WHERE id = ?",
        (student_id,)
    )
    student = cursor.fetchone()

    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    # ---------- Attendance ----------
    cursor.execute("""
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present
        FROM attendance
        WHERE student_id = ?
    """, (student_id,))
    att = cursor.fetchone()

    attendance_percent = (
        round((att["present"] / att["total"]) * 100, 2)
        if att["total"] else 0
    )

    # ---------- Fees ----------
    cursor.execute("""
        SELECT total_fees, fees_paid
        FROM students WHERE id = ?
    """, (student_id,))
    fees = cursor.fetchone()

    outstanding = fees["total_fees"] - fees["fees_paid"]

    # ---------- Results ----------
    cursor.execute("""
        SELECT subject,
               AVG((obtained_marks * 100.0) / total_marks) AS avg_percentage
        FROM results
        WHERE student_id = ?
        GROUP BY subject
    """, (student_id,))
    subjects = cursor.fetchall()

    overall = (
        round(sum(s["avg_percentage"] for s in subjects) / len(subjects), 2)
        if subjects else 0
    )

    conn.close()

    return jsonify({
        "student": dict(student),
        "attendance_percentage": attendance_percent,
        "fees": {
            "total": fees["total_fees"],
            "paid": fees["fees_paid"],
            "outstanding": outstanding
        },
        "subjects": [dict(s) for s in subjects],
        "overall_percentage": overall
    })
@performance_bp.route("/student/growth/<int:student_id>", methods=["GET"])
def student_growth(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subject, exam_date,
               ROUND((obtained_marks * 100.0) / total_marks, 2) AS percentage
        FROM results
        WHERE student_id = ?
        ORDER BY subject, exam_date
    """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

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

    return jsonify(growth)