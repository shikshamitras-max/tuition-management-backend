from flask import Blueprint, request, jsonify
from database.db import get_db_connection

student_bp = Blueprint("student_bp", __name__)

# -------------------------------
# ADD STUDENT
# -------------------------------
@student_bp.route("/students", methods=["POST"])
def add_student():
    try:
        data = request.get_json(force=True)

        # Required fields
        required = ["name", "batch", "phone", "parent_phone", "total_fees"]

        for field in required:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students 
            (name, phone, email, batch, total_fees, fees_paid, parent_phone)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """, (
            data["name"],
            data["phone"],
            data.get("email"),
            data["batch"],
            data["total_fees"],
            data["parent_phone"]
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
