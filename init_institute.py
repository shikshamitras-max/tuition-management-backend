from database.db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# -----------------------------------
# CREATE INSTITUTE SETTINGS TABLE
# -----------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS institute_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    institute_name TEXT NOT NULL,
    address TEXT NOT NULL,
    contact TEXT NOT NULL,
    logo_path TEXT,
    signature_name TEXT
)
""")

# -----------------------------------
# INSERT DEFAULT INSTITUTE DATA (ONLY ONCE)
# -----------------------------------
cursor.execute("""
INSERT INTO institute_settings (
    institute_name,
    address,
    contact,
    logo_path,
    signature_name
)
SELECT
    'Shiksha Mitra',
    'Shop-110/111, 1st floor, Vitoria Heights, Ugat Canal Jn., Jahangirpura, Surat-395005',
    '9712212215',
    'static/logo.png',
    'Director'
WHERE NOT EXISTS (SELECT 1 FROM institute_settings)
""")

conn.commit()
conn.close()

print("✅ Institute settings created & initialized safely")