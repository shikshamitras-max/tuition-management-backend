from flask import Blueprint, request, jsonify
from database.db import get_db_connection
from datetime import date

fees_bp = Blueprint("fees_bp", __name__)

# --------------------------------------------------
# ADD FEES + AUTO INVOICE
# --------------------------------------------------
@fees_bp.route("/fees", methods=["POST"])
def add_fees():
    data = request.json

    # -------- VALIDATIONS --------
    if not data or "student_id" not in data or "amount" not in data:
        return jsonify({"error": "student_id and amount are required"}), 400

    if not isinstance(data["amount"], int) or data["amount"] <= 0:
        return jsonify({"error": "Amount must be a positive number"}), 400

    student_id = data["student_id"]
    amount = data["amount"]
    payment_mode = data.get("payment_mode", "Cash")
    fee_date = data.get("date", date.today().isoformat())

    conn = get_db_connection()
    cursor = conn.cursor()

    # -------- CHECK STUDENT EXISTS --------
    cursor.execute(
        "SELECT id, fees_paid FROM students WHERE id = ?",
        (student_id,)
    )
    student = cursor.fetchone()

    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    # -------- PREVENT DUPLICATE PAYMENT SAME DAY --------
    cursor.execute("""
        SELECT id FROM fees
        WHERE student_id = ? AND date = ?
    """, (student_id, fee_date))

    if cursor.fetchone():
        conn.close()
        return jsonify({
            "error": "Fees already recorded for this student on this date"
        }), 409

    # -------- INSERT FEES PAYMENT --------
    cursor.execute("""
        INSERT INTO fees (student_id, amount, date)
        VALUES (?, ?, ?)
    """, (student_id, amount, fee_date))

    fees_id = cursor.lastrowid

    # -------- UPDATE STUDENT TOTAL FEES PAID --------
    new_total_paid = student["fees_paid"] + amount

    cursor.execute("""
        UPDATE students
        SET fees_paid = ?
        WHERE id = ?
    """, (new_total_paid, student_id))

    # -------- GENERATE INVOICE --------
    cursor.execute("SELECT COUNT(*) FROM invoices")
    invoice_count = cursor.fetchone()[0] + 1
    invoice_number = f"INV-2025-{invoice_count:04d}"

    TOTAL_FEES = 12000   # 🔹 You can make this dynamic later
    balance = TOTAL_FEES - new_total_paid

    cursor.execute("""
        INSERT INTO invoices (
            invoice_number,
            student_id,
            fees_id,
            payment_mode,
            invoice_date,
            total_fees,
            total_paid,
            balance
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_number,
        student_id,
        fees_id,
        payment_mode,
        fee_date,
        TOTAL_FEES,
        new_total_paid,
        balance
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Fees recorded & invoice generated successfully",
        "invoice_number": invoice_number,
        "total_paid": new_total_paid,
        "balance": balance
    }), 201


# --------------------------------------------------
# GET FEES BY STUDENT
# --------------------------------------------------
@fees_bp.route("/fees/<int:student_id>", methods=["GET"])
def get_fees_by_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, amount, date
        FROM fees
        WHERE student_id = ?
        ORDER BY date DESC
    """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


# --------------------------------------------------
# GET ALL FEES RECORDS
# --------------------------------------------------
@fees_bp.route("/fees", methods=["GET"])
def get_all_fees():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT students.name,
               fees.amount,
               fees.date
        FROM fees
        JOIN students ON students.id = fees.student_id
        ORDER BY fees.date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


# --------------------------------------------------
# STUDENT FEES SUMMARY
# --------------------------------------------------
@fees_bp.route("/fees/summary/<int:student_id>", methods=["GET"])
def fees_summary(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT students.name,
               COUNT(fees.id) AS payments,
               COALESCE(SUM(fees.amount), 0) AS total_paid
        FROM students
        LEFT JOIN fees ON students.id = fees.student_id
        WHERE students.id = ?
    """, (student_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(row))


# --------------------------------------------------
# DELETE FEES RECORD (ADMIN)
# --------------------------------------------------
@fees_bp.route("/fees/<int:fee_id>", methods=["DELETE"])
def delete_fee(fee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT student_id, amount FROM fees WHERE id = ?",
        (fee_id,)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Fee record not found"}), 404

    student_id = row["student_id"]
    amount = row["amount"]

    cursor.execute("DELETE FROM fees WHERE id = ?", (fee_id,))

    cursor.execute("""
        UPDATE students
        SET fees_paid = fees_paid - ?
        WHERE id = ?
    """, (amount, student_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Fee record deleted successfully"})


# --------------------------------------------------
# GET ALL INVOICES
# --------------------------------------------------
@fees_bp.route("/invoices", methods=["GET"])
def get_all_invoices():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT invoices.invoice_number,
               students.name,
               invoices.payment_mode,
               invoices.invoice_date,
               invoices.total_paid,
               invoices.balance
        FROM invoices
        JOIN students ON students.id = invoices.student_id
        ORDER BY invoices.id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])
from flask import send_file
from utils.invoice_pdf import generate_invoice_pdf

@fees_bp.route("/invoice/<invoice_number>", methods=["GET"])
def download_invoice(invoice_number):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get invoice
    cursor.execute("""
        SELECT * FROM invoices WHERE invoice_number = ?
    """, (invoice_number,))
    invoice = cursor.fetchone()

    if not invoice:
        conn.close()
        return jsonify({"error": "Invoice not found"}), 404

    # Get student
    cursor.execute("""
        SELECT * FROM students WHERE id = ?
    """, (invoice["student_id"],))
    student = cursor.fetchone()

    # Get institute info
    cursor.execute("""
        SELECT * FROM institute_settings LIMIT 1
    """)
    institute = cursor.fetchone()

    conn.close()

    if not institute:
        return jsonify({"error": "Institute settings not found"}), 500

    pdf_path = generate_invoice_pdf(
        dict(invoice), dict(student), dict(institute)
    )

    return send_file(pdf_path, as_attachment=True)
