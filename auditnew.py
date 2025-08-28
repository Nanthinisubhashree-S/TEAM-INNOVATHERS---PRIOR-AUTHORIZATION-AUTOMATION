# auditnew.py
import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "prior_auth.db")

def ensure_audit_table():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                patient_id TEXT,
                treatment_name TEXT,
                icd10_code TEXT,
                provider_npi TEXT,
                rule_status TEXT,
                proof_status TEXT,
                final_decision TEXT
            )
        """)
        conn.commit()


def log_audit(patient_id, treatment_name, icd10_code, provider_npi,
              rule_status, proof_status, final_decision):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO audit_log
            (timestamp, patient_id, treatment_name, icd10_code, provider_npi, rule_status, proof_status, final_decision)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            patient_id or "",
            treatment_name or "",
            icd10_code or "",
            provider_npi or "",
            rule_status or "",
            proof_status or "",
            final_decision or ""
        ))
        
        conn.commit()
