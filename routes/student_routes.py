from flask import Blueprint, request, jsonify
from database.db import get_db_connection

student_bp = Blueprint("student_bp", __name__)

# -------------------------------
# ADD STUDENT
# -------------------------------
@student_bp.route("/students", methods=["POST"])
def add_student():
    data = request.json

    if not data or "name" not in data or "total_fees" not in data:
        return jsonify({"error": "name and total_fees required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students (name, phone, email, batch, total_fees, fees_paid)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (
        data["name"],
        data.get("phone"),
        data.get("email"),
        data.get("batch"),
        data["total_fees"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Student added successfully"}), 201


# -------------------------------
# GET STUDENTS
# -------------------------------
@student_bp.route("/students", methods=["GET"])
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@student_bp.route("/students/<int:student_id>/fees", methods=["PUT"])
def update_total_fees(student_id):
    data = request.json

    if "total_fees" not in data:
        return jsonify({"error": "total_fees required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET total_fees = ?
        WHERE id = ?
    """, (data["total_fees"], student_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Total fees updated successfully"})
