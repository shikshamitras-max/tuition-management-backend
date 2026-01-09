from database.db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS institute (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL,
    signature TEXT NOT NULL
)
""")

cursor.execute("""
INSERT INTO institute (name, address, phone, signature)
SELECT 'ABC Tuition Classes',
       'Main Road, City',
       '9999999999',
       'Director'
WHERE NOT EXISTS (SELECT 1 FROM institute)
""")

conn.commit()
conn.close()

print("✅ Institute table created & data inserted")
