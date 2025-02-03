import sqlite3

conn = sqlite3.connect("database.db")  # Creates a new database file
c = conn.cursor()

# Create a table
c.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()