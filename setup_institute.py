import sqlite3
from pathlib import Path

# Path to database
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tuition.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create institute_settings table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS institute_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    institute_name TEXT NOT NULL,
    address TEXT NOT NULL,
    contact TEXT NOT NULL,
    logo_path TEXT,
    signature_name TEXT NOT NULL
)
""")

# Check if already exists
cursor.execute("SELECT COUNT(*) FROM institute_settings")
count = cursor.fetchone()[0]

if count == 0:
    cursor.execute("""
    INSERT INTO institute_settings (
        institute_name,
        address,
        contact,
        signature_name
    ) VALUES (?, ?, ?, ?)
    """, (
        "Shiksha Mitra Tuition Classes",
        "Main Road, City Name",
        "9876543210",
        "Authorized Signatory"
    ))

    print("✅ Institute setup completed successfully")
else:
    print("ℹ Institute already configured (no action needed)")

conn.commit()
conn.close()