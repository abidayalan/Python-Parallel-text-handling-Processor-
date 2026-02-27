import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS texts (
    id INTEGER PRIMARY KEY,
    sentence TEXT,
    score INTEGER
)
""")

conn.commit()
conn.close()
