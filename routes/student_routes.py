from flask import Blueprint, request, jsonify
from database.db import get_db_connection

student_bp = Blueprint("student_bp", __name__)

# -------------------------------
# ADD STUDENT
# -------------------------------
@student_bp.route("/students", methods=["POST"])
def add_student():
    try:
        data = request.json

        if not data or "name" not in data or "total_fees" not in data:
            return jsonify({"error": "name and total_fees required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students 
            (name, phone, parent_phone, email, batch, total_fees, fees_paid)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (
            data["name"],
            data.get("phone"),
            data.get("parent_phone"),   # optional
            data.get("email"),
            data.get("batch"),
            data["total_fees"]
        ))

        conn.commit()
        conn.close()

        return jsonify({"message": "Student added successfully"}), 201

    except Exception as e:
        print("STUDENT INSERT ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# -------------------------------
# GET STUDENTS
# -------------------------------
@student_bp.route("/students", methods=["GET"])
def get_students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()
        conn.close()

        return jsonify([dict(row) for row in rows])

    except Exception as e:
        print("GET STUDENTS ERROR:", str(e))
        return jsonify({"error": "Failed to fetch students"}), 500


# -------------------------------
# UPDATE TOTAL FEES
# -------------------------------
@student_bp.route("/students/<int:student_id>/fees", methods=["PUT"])
def update_total_fees(student_id):
    try:
        data = request.json

        if not data or "total_fees" not in data:
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

    except Exception as e:
        print("UPDATE FEES ERROR:", str(e))
        return jsonify({"error": "Failed to update fees"}), 500