from flask import Blueprint, request, jsonify
from database.db import get_db_connection
import jwt
import datetime

SECRET_KEY = "parent-secret-key"

parent_auth_bp = Blueprint("parent_auth_bp", __name__)

@parent_auth_bp.route("/parent/login", methods=["POST"])
def parent_login():
    data = request.json
    phone = data.get("phone")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, batch
        FROM students
        WHERE parent_phone = ? AND parent_password = ?
    """, (phone, password))

    parent = cursor.fetchone()
    conn.close()

    if not parent:
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "student_id": parent["id"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "token": token,
        "student": {
            "id": parent["id"],
            "name": parent["name"],
            "batch": parent["batch"]
        }
    })