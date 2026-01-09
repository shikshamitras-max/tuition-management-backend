from flask import Blueprint, request, jsonify
from database.db import get_db_connection

exam_bp = Blueprint("exam_bp", __name__)

# -----------------------------------
# ADD SUBJECT
# -----------------------------------
@exam_bp.route("/subjects", methods=["POST"])
def add_subject():
    data = request.json
    if "name" not in data:
        return jsonify({"error": "Subject name required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO subjects (name) VALUES (?)", (data["name"],))
        conn.commit()
    except:
        conn.close()
        return jsonify({"error": "Subject already exists"}), 409

    conn.close()
    return jsonify({"message": "Subject added successfully"}), 201


# -----------------------------------
# ADD EXAM
# -----------------------------------
@exam_bp.route("/exams", methods=["POST"])
def add_exam():
    data = request.json

    required = ["name", "exam_date", "batch"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO exams (name, exam_date, batch, exam_type)
        VALUES (?, ?, ?, ?)
    """, (
        data["name"],
        data["exam_date"],
        data["batch"],
        data.get("exam_type")
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Exam created successfully"}), 201


# -----------------------------------
# ADD RESULT / MARKS
# -----------------------------------
@exam_bp.route("/results", methods=["POST"])
def add_result():
    data = request.json

    required = ["student_id", "exam_id", "subject_id", "total_marks", "obtained_marks"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO results
        (student_id, exam_id, subject_id, total_marks, obtained_marks)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["student_id"],
        data["exam_id"],
        data["subject_id"],
        data["total_marks"],
        data["obtained_marks"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Result added successfully"}), 201
# -----------------------------------
# GET STUDENT PERFORMANCE REPORT
# -----------------------------------
@exam_bp.route("/results/student/<int:student_id>", methods=["GET"])
def get_student_performance(student_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            exams.name AS exam_name,
            exams.exam_date,
            exams.exam_type,
            subjects.name AS subject,
            results.total_marks,
            results.obtained_marks,
            ROUND(
                (results.obtained_marks * 100.0) / results.total_marks, 2
            ) AS percentage
        FROM results
        JOIN exams ON exams.id = results.exam_id
        JOIN subjects ON subjects.id = results.subject_id
        WHERE results.student_id = ?
        ORDER BY exams.exam_date
    """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

# -----------------------------------
# STUDENT GROWTH ANALYSIS (SUBJECT-WISE)
# -----------------------------------
@exam_bp.route("/results/growth/<int:student_id>", methods=["GET"])
def student_growth(student_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            subjects.name AS subject,
            exams.exam_date,
            ROUND(
                (results.obtained_marks * 100.0) / results.total_marks, 2
            ) AS percentage
        FROM results
        JOIN exams ON exams.id = results.exam_id
        JOIN subjects ON subjects.id = results.subject_id
        WHERE results.student_id = ?
        ORDER BY subjects.name, exams.exam_date
    """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    growth_report = {}
    previous = {}

    for row in rows:
        subject = row["subject"]
        percent = row["percentage"]

        if subject not in growth_report:
            growth_report[subject] = []
            previous[subject] = None

        change = None
        if previous[subject] is not None:
            change = round(percent - previous[subject], 2)

        growth_report[subject].append({
            "exam_date": row["exam_date"],
            "percentage": percent,
            "change": change
        })

        previous[subject] = percent

    return jsonify(growth_report)