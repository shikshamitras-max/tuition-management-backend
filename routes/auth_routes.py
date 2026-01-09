from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db_connection

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
    """, (
        data["username"],
        generate_password_hash(data["password"]),
        data["role"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "User registered"})


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (data["username"],))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], data["password"]):
        return jsonify({"message": "Login successful", "role": user["role"]})

    return jsonify({"error": "Invalid credentials"}), 401