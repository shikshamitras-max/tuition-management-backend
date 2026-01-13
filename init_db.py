import sqlite3
from pathlib import Path

# -------------------------------
# DATABASE PATH (IMPORTANT)
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tuition.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -------------------------------
# STUDENTS TABLE
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    batch TEXT,
    fees_paid INTEGER DEFAULT 0
)
""")

# -------------------------------
# FEES PAYMENTS TABLE
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

# -------------------------------
# USERS (AUTH)
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# -------------------------------
# ATTENDANCE TABLE
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT CHECK(status IN ('Present','Absent')) NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

# -------------------------------
# INSTITUTE SETTINGS (ONE-TIME)
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS institute_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    institute_name TEXT NOT NULL,
    address TEXT NOT NULL,
    contact TEXT,
    logo_path TEXT,
    signature_name TEXT
)
""")

# -------------------------------
# INVOICES TABLE
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    student_id INTEGER NOT NULL,
    fees_id INTEGER NOT NULL,
    payment_mode TEXT CHECK(payment_mode IN ('Cash','Online','Cheque')) NOT NULL,
    invoice_date TEXT NOT NULL,
    total_fees INTEGER NOT NULL,
    total_paid INTEGER NOT NULL,
    balance INTEGER NOT NULL,
    pdf_path TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(fees_id) REFERENCES fees(id)
)
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully (students, fees, users, attendance, invoices)")

import sqlite3

conn = sqlite3.connect("tuition.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE students 
ADD COLUMN total_fees INTEGER DEFAULT 0
""")

conn.commit()
conn.close()

print("total_fees column added")

import sqlite3

conn = sqlite3.connect("tuition.db")
cursor = conn.cursor()

# Add total_fees if missing
try:
    cursor.execute("ALTER TABLE students ADD COLUMN total_fees INTEGER DEFAULT 0")
except:
    pass

# Add parent_phone if missing
try:
    cursor.execute("ALTER TABLE students ADD COLUMN parent_phone TEXT")
except:
    pass

conn.commit()
conn.close()

print("Database upgraded")