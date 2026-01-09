from flask import Blueprint, jsonify
from database.db import get_db_connection

admin_dashboard_bp = Blueprint("admin_dashboard_bp", __name__)

@admin_dashboard_bp.route("/admin/dashboard/summary", methods=["GET"])
def admin_dashboard_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total students
    cursor.execute("SELECT COUNT(*) as total FROM students")
    total_students = cursor.fetchone()["total"]

    # Fees collected
    cursor.execute("SELECT SUM(fees_paid) as collected FROM students")
    fees_collected = cursor.fetchone()["collected"] or 0

    # Total fees
    cursor.execute("SELECT SUM(total_fees) as total FROM students")
    total_fees = cursor.fetchone()["total"] or 0

    fees_pending = total_fees - fees_collected

    # Attendance %
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN status='Present' THEN 1 END) * 100.0 / COUNT(*) 
            AS percentage
        FROM attendance
    """)
    attendance_percentage = cursor.fetchone()["percentage"] or 0

    conn.close()

    return jsonify({
        "students": total_students,
        "fees_collected": fees_collected,
        "fees_pending": fees_pending,
        "attendance_percentage": round(attendance_percentage, 2)
    })
@admin_dashboard_bp.route("/admin/dashboard/fees-monthly", methods=["GET"])
def monthly_fees_chart():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            substr(date, 1, 7) AS month,
            SUM(amount) AS total
        FROM fees
        GROUP BY month
        ORDER BY month
    """)

    rows = cursor.fetchall()
    conn.close()

    return jsonify([
        {"month": row["month"], "amount": row["total"]}
        for row in rows
    ])