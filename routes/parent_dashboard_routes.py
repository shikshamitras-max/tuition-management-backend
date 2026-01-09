from flask import Blueprint, jsonify
from database.db import get_db_connection

parent_dashboard_bp = Blueprint("parent_dashboard_bp", __name__)
@parent_dashboard_bp.route("/parent/dashboard/<int:student_id>", methods=["GET"])
def parent_dashboard(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # -------- Student --------
    cursor.execute("""
        SELECT name, batch, fees_paid, total_fees
        FROM students
        WHERE id = ?
    """, (student_id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return {"error": "Student not found"}, 404

    # -------- Attendance --------
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_days,
            COUNT(*) AS total_days
        FROM attendance
        WHERE student_id = ?
    """, (student_id,))
    attendance = cursor.fetchone()

    attendance_percentage = 0
    if attendance["total_days"]:
        attendance_percentage = round(
            (attendance["present_days"] * 100) / attendance["total_days"], 2
        )

    # -------- Performance --------
    cursor.execute("""
        SELECT 
            SUM(obtained_marks) AS obtained,
            SUM(total_marks) AS total
        FROM results
        WHERE student_id = ?
    """, (student_id,))
    perf = cursor.fetchone()

    percentage = 0
    remark = "No Data"
    if perf["total"]:
        percentage = round((perf["obtained"] * 100) / perf["total"], 2)
        if percentage >= 85:
            remark = "Excellent"
        elif percentage >= 60:
            remark = "Good"
        else:
            remark = "Needs Improvement"

    conn.close()

    return jsonify({
        "student": {
            "name": student["name"],
            "class": student["batch"]
        },
        "attendance": f"{attendance_percentage}%",
        "fees": {
            "total": student["total_fees"],
            "paid": student["fees_paid"],
            "outstanding": student["total_fees"] - student["fees_paid"]
        },
        "performance": {
            "average_percentage": percentage,
            "remark": remark
        },
        "downloads": {
            "report_card_pdf": f"/report-card/pdf/{student_id}",
            "invoice_pdf": f"/invoice/{student_id}"
        }
    })