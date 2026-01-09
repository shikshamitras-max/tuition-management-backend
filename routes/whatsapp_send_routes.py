from flask import Blueprint, jsonify
from twilio.rest import Client
from dotenv import load_dotenv
import os

from database.db import get_db_connection

load_dotenv()

whatsapp_send_bp = Blueprint("whatsapp_send_bp", __name__)

# ✅ Twilio credentials from .env
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")

client = Client(account_sid, auth_token)

@whatsapp_send_bp.route("/send/whatsapp/report/<int:student_id>", methods=["GET"])
def send_report_whatsapp(student_id):

    from database.db import get_db_connection

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get student + parent phone
    cursor.execute("""
        SELECT name, parent_phone
        FROM students
        WHERE id = ?
    """, (student_id,))

    student = cursor.fetchone()
    conn.close()

    if not student or not student["parent_phone"]:
        return jsonify({"error": "Parent phone not found"}), 404

    # WhatsApp number format
    to_number = f"whatsapp:+91{student['parent_phone']}"

    # PDF URL (local)
    pdf_url = f"http://127.0.0.1:5000/static/report_card_student_{student_id}.pdf"

    # Send WhatsApp message with link
    message = client.messages.create(
        body=(
            f"📘 *Report Card*\n\n"
            f"Student: {student['name']}\n\n"
            f"Download PDF 👇\n{pdf_url}"
        ),
        from_=whatsapp_from,
        to=to_number
    )

    return jsonify({
        "status": "sent",
        "to": to_number,
        "pdf": pdf_url,
        "sid": message.sid
    })
