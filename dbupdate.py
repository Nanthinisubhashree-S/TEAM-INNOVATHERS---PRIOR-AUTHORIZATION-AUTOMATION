import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "prior_auth.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DELETE FROM provider_table;")

providers = [
    (1003008533, "Cardiologist", 28, 28, "2025-03-10", "2029-10-07"),
    (1003000126, "Orthologist", 12, 12, "2020-04-06", "2029-07-09"),
    (1003008517, "Ophthalmologist", 13, 13, "2023-08-17", "2027-09-19"),
    (1003008269, "Oncologist", 13, 13, "2020-03-18", "2029-07-10"),
    (1003000142, "Nephrologist", 41, 41, "2021-04-20", "2029-01-17")
]

cursor.executemany("""
INSERT INTO provider_table 
(Rndrng_NPI, Rndrng_Prvdr_Type, Tot_Srvcs, Tot_Benes, Start_date, End_date)
VALUES (?, ?, ?, ?, ?, ?);
""", providers)

conn.commit()
conn.close()

print("✅ provider_table updated with the first 5 specified records.")
