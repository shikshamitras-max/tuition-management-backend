from flask import Blueprint, request, jsonify, send_file
from database.db import get_db_connection
from datetime import date
from utils.invoice_pdf import generate_invoice_pdf

fees_bp = Blueprint("fees_bp", __name__)

# --------------------------------------------------
# ADD FEES + AUTO INVOICE
# --------------------------------------------------
@fees_bp.route("/fees", methods=["POST"])
def add_fees():
    data = request.json

    if not data or "student_id" not in data or "amount" not in data:
        return jsonify({"error": "student_id and amount are required"}), 400

    if not isinstance(data["amount"], int) or data["amount"] <= 0:
        return jsonify({"error": "Amount must be positive integer"}), 400

    student_id = data["student_id"]
    amount = data["amount"]
    payment_mode = data.get("payment_mode", "Cash")
    fee_date = data.get("date", date.today().isoformat())

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get student
    cursor.execute(
        "SELECT id, fees_paid, total_fees FROM students WHERE id = ?",
        (student_id,)
    )
    student = cursor.fetchone()

    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    total_fees = student["total_fees"]
    fees_paid = student["fees_paid"]

    if total_fees is None or total_fees <= 0:
        conn.close()
        return jsonify({"error": "Student total fees not set"}), 400

    new_total_paid = fees_paid + amount

    if new_total_paid > total_fees:
        conn.close()
        return jsonify({"error": "Payment exceeds total fees"}), 400

    # Prevent same-day duplicate
    cursor.execute("""
        SELECT id FROM fees
        WHERE student_id = ? AND date = ?
    """, (student_id, fee_date))

    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Fees already recorded today"}), 409

    # Insert fees
    cursor.execute("""
        INSERT INTO fees (student_id, amount, date)
        VALUES (?, ?, ?)
    """, (student_id, amount, fee_date))

    fees_id = cursor.lastrowid

    # Update paid amount
    cursor.execute("""
        UPDATE students
        SET fees_paid = ?
        WHERE id = ?
    """, (new_total_paid, student_id))

    balance = total_fees - new_total_paid

    # Invoice number
    cursor.execute("SELECT COUNT(*) FROM invoices")
    count = cursor.fetchone()[0] + 1
    invoice_number = f"INV-2025-{count:04d}"

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
        total_fees,
        new_total_paid,
        balance
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Fees recorded & invoice generated",
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
# GET ALL FEES
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
# FEES SUMMARY
# --------------------------------------------------
@fees_bp.route("/fees/summary/<int:student_id>", methods=["GET"])
def fees_summary(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT students.name,
               students.total_fees,
               students.fees_paid,
               (students.total_fees - students.fees_paid) AS balance
        FROM students
        WHERE students.id = ?
    """, (student_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(row))


# --------------------------------------------------
# DELETE FEE
# --------------------------------------------------
@fees_bp.route("/fees/<int:fee_id>", methods=["DELETE"])
def delete_fee(fee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT student_id, amount FROM fees WHERE id = ?", (fee_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Fee not found"}), 404

    cursor.execute("DELETE FROM fees WHERE id = ?", (fee_id,))
    cursor.execute("""
        UPDATE students
        SET fees_paid = fees_paid - ?
        WHERE id = ?
    """, (row["amount"], row["student_id"]))

    conn.commit()
    conn.close()
    return jsonify({"message": "Fee deleted"})


# --------------------------------------------------
# ALL INVOICES
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


# --------------------------------------------------
# DOWNLOAD INVOICE
# --------------------------------------------------
@fees_bp.route("/invoice/<invoice_number>", methods=["GET"])
def download_invoice(invoice_number):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
    invoice = cursor.fetchone()

    if not invoice:
        conn.close()
        return jsonify({"error": "Invoice not found"}), 404

    cursor.execute("SELECT * FROM students WHERE id = ?", (invoice["student_id"],))
    student = cursor.fetchone()

    cursor.execute("SELECT * FROM institute_settings LIMIT 1")
    institute = cursor.fetchone()

    conn.close()

    pdf_path = generate_invoice_pdf(dict(invoice), dict(student), dict(institute))
    return send_file(pdf_path, as_attachment=True)