from flask import Blueprint, jsonify
from database.db import get_db_connection

report_bp = Blueprint("report_bp", __name__)

@report_bp.route("/report-card/<int:student_id>", methods=["GET"])
def report_card(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ---------------- STUDENT INFO ----------------
    cursor.execute("""
        SELECT name, batch
        FROM students
        WHERE id = ?
    """, (student_id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    # ---------------- RESULTS ----------------
    cursor.execute("""
        SELECT
            subject,
            exam_name,
            total_marks,
            obtained_marks,
            ROUND((obtained_marks * 100.0) / total_marks, 2) AS percentage
        FROM results
        WHERE student_id = ?
        ORDER BY subject, exam_date
    """, (student_id,))

    rows = cursor.fetchall()

    subjects = []
    total_obtained = 0
    total_marks = 0

    for row in rows:
        subjects.append({
            "subject": row["subject"],
            "exam_name": row["exam_name"],
            "total_marks": row["total_marks"],
            "obtained_marks": row["obtained_marks"],
            "percentage": row["percentage"]
        })

        total_obtained += row["obtained_marks"]
        total_marks += row["total_marks"]

    overall_percentage = round((total_obtained / total_marks) * 100, 2) if total_marks else 0

    # ---------------- REMARK ----------------
    if overall_percentage >= 75:
        remark = "Excellent"
    elif overall_percentage >= 50:
        remark = "Good"
    else:
        remark = "Needs Improvement"

    conn.close()

    return jsonify({
        "student": {
            "name": student["name"],
            "batch": student["batch"]
        },
        "subjects": subjects,
        "overall": {
            "total_marks": total_marks,
            "obtained_marks": total_obtained,
            "percentage": overall_percentage,
            "remark": remark
        }
    })