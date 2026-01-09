from flask import Blueprint, jsonify
from database.db import get_db_connection

monthly_analytics_bp = Blueprint("monthly_analytics_bp", __name__)

@monthly_analytics_bp.route(
    "/analytics/monthly/<int:student_id>/<int:year>",
    methods=["GET"]
)
def monthly_performance(student_id, year):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            strftime('%m', exam_date) AS month,
            COUNT(DISTINCT exam_name) AS total_exams,
            SUM(total_marks) AS total_marks,
            SUM(obtained_marks) AS obtained_marks,
            ROUND(
                (SUM(obtained_marks) * 100.0) / SUM(total_marks),
                2
            ) AS percentage
        FROM results
        WHERE student_id = ?
          AND strftime('%Y', exam_date) = ?
        GROUP BY month
        ORDER BY month
    """, (student_id, str(year)))

    rows = cursor.fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append({
            "month": r["month"],
            "total_exams": r["total_exams"],
            "total_marks": r["total_marks"],
            "obtained_marks": r["obtained_marks"],
            "percentage": r["percentage"]
        })

    return jsonify({
        "student_id": student_id,
        "year": year,
        "monthly_performance": data
    })
