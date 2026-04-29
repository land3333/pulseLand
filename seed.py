"""
seed.py — Populate database.db with sample data for demo.
Run once:  python seed.py
"""
import sqlite3, os, random

DB = os.path.join(os.path.dirname(__file__), 'database.db')

# Initialise DB
conn = sqlite3.connect(DB)
conn.execute('''
    CREATE TABLE IF NOT EXISTS users_data (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        age      INTEGER NOT NULL,
        activity REAL    NOT NULL,
        sleep    REAL    NOT NULL,
        gender   TEXT    NOT NULL,
        stress   INTEGER NOT NULL,
        weight   REAL    NOT NULL,
        height   REAL    NOT NULL,
        bmi      REAL    NOT NULL
    )
''')

samples = [
    (28, 90,  7.5, 'M', 3, 72,  1.78, 22.7),
    (35, 45,  6.0, 'F', 6, 65,  1.65, 23.9),
    (52, 20,  5.5, 'M', 8, 95,  1.72, 32.1),
    (24, 150, 8.0, 'F', 2, 58,  1.62, 22.1),
    (41, 60,  7.0, 'M', 5, 82,  1.80, 25.3),
    (30, 120, 7.5, 'F', 4, 60,  1.68, 21.3),
    (60, 15,  6.5, 'M', 7, 88,  1.69, 30.8),
    (22, 200, 8.5, 'M', 1, 68,  1.75, 22.2),
    (47, 30,  5.0, 'F', 9, 78,  1.60, 30.5),
    (33, 75,  7.0, 'Other',4, 70, 1.70, 24.2),
]

conn.executemany(
    'INSERT INTO users_data (age,activity,sleep,gender,stress,weight,height,bmi) VALUES (?,?,?,?,?,?,?,?)',
    samples
)
conn.commit()
conn.close()
print(f"✓ {len(samples)} enregistrements insérés dans {DB}")
