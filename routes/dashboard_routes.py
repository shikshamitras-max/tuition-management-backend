from flask import Blueprint, jsonify
from database.db import get_db_connection
from datetime import date

dashboard_bp = Blueprint("dashboard_bp", __name__)

# --------------------------------------------------
# DASHBOARD SUMMARY
# --------------------------------------------------
@dashboard_bp.route("/dashboard/summary", methods=["GET"])
def dashboard_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total students
    cursor.execute("SELECT COUNT(*) AS total_students FROM students")
    total_students = cursor.fetchone()["total_students"]

    # Total fees collected
    cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total_fees FROM fees")
    total_fees = cursor.fetchone()["total_fees"]

    # Today attendance count
    today = date.today().isoformat()
    cursor.execute("""
        SELECT COUNT(*) AS present_today
        FROM attendance
        WHERE date = ? AND status = 'Present'
    """, (today,))
    present_today = cursor.fetchone()["present_today"]

    conn.close()

    return jsonify({
        "total_students": total_students,
        "total_fees_collected": total_fees,
        "present_today": present_today
    })


# --------------------------------------------------
# MONTHLY FEES REPORT
# --------------------------------------------------
@dashboard_bp.route("/dashboard/monthly-fees", methods=["GET"])
def monthly_fees_report():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT strftime('%Y-%m', date) AS month,
               SUM(amount) AS total_amount
        FROM fees
        GROUP BY month
        ORDER BY month DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


# --------------------------------------------------
# STUDENT ATTENDANCE SUMMARY
# --------------------------------------------------
@dashboard_bp.route("/dashboard/attendance-summary", methods=["GET"])
def attendance_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT students.name,
               COUNT(attendance.id) AS total_days,
               SUM(CASE WHEN attendance.status = 'Present' THEN 1 ELSE 0 END) AS present_days
        FROM students
        LEFT JOIN attendance ON students.id = attendance.student_id
        GROUP BY students.id
    """)

    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])