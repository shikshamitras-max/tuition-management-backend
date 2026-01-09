from flask import Blueprint, request, jsonify
from database.db import get_db_connection
from datetime import date

attendance_bp = Blueprint("attendance_bp", __name__)

@attendance_bp.route("/attendance", methods=["POST"])
def mark_attendance():
    data = request.json
    today = date.today().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attendance (student_id, date, status)
        VALUES (?, ?, ?)
    """, (
        data["student_id"],
        today,
        data["status"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Attendance marked"})


@attendance_bp.route("/attendance", methods=["GET"])
def get_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT attendance.id, students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON students.id = attendance.student_id
    """)
    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])