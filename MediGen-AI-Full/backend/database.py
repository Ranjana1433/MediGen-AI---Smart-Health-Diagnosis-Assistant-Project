"""
SQLite layer for diagnosis history (linked to the logged-in user).
User accounts and sessions are handled separately in auth.py.
"""
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "history.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS diagnosis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            name TEXT,
            symptoms TEXT,
            predicted_disease TEXT,
            confidence REAL,
            severity TEXT,
            explanation TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            patient_name TEXT,
            doctor_id TEXT,
            doctor_name TEXT,
            specialty TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            reason TEXT,
            status TEXT DEFAULT 'Confirmed',
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


# ---------------- Diagnosis history ----------------

def save_record(username, name, symptoms, disease, confidence, severity, explanation):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO diagnosis_history
        (username, name, symptoms, predicted_disease, confidence, severity, explanation, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            name,
            ",".join(symptoms),
            disease,
            confidence,
            severity,
            explanation,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    record_id = cur.lastrowid
    conn.close()
    return record_id


def get_history(username: str = None, limit: int = 20):
    conn = _connect()
    cur = conn.cursor()
    if username:
        cur.execute(
            "SELECT * FROM diagnosis_history WHERE username = ? ORDER BY id DESC LIMIT ?",
            (username, limit),
        )
    else:
        cur.execute(
            "SELECT * FROM diagnosis_history ORDER BY id DESC LIMIT ?", (limit,)
        )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


# ---------------- Appointments ----------------

def save_appointment(username, patient_name, doctor_id, doctor_name, specialty,
                      appointment_date, appointment_time, reason):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO appointments
        (username, patient_name, doctor_id, doctor_name, specialty,
         appointment_date, appointment_time, reason, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?)
        """,
        (
            username,
            patient_name,
            doctor_id,
            doctor_name,
            specialty,
            appointment_date,
            appointment_time,
            reason,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    appointment_id = cur.lastrowid
    conn.close()
    return appointment_id


def get_appointments(username: str = None, limit: int = 50):
    conn = _connect()
    cur = conn.cursor()
    if username:
        cur.execute(
            """SELECT * FROM appointments WHERE username = ?
               ORDER BY appointment_date ASC, appointment_time ASC LIMIT ?""",
            (username, limit),
        )
    else:
        cur.execute(
            """SELECT * FROM appointments
               ORDER BY appointment_date ASC, appointment_time ASC LIMIT ?""",
            (limit,),
        )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def cancel_appointment(appointment_id: int, username: str):
    """Only the owner can cancel their own appointment."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "UPDATE appointments SET status = 'Cancelled' WHERE id = ? AND username = ?",
        (appointment_id, username),
    )
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0

