from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

try:
    import mysql.connector
    from mysql.connector import IntegrityError as MySQLIntegrityError
except Exception:  # pragma: no cover - optional dependency during local setup
    mysql = None
    MySQLIntegrityError = Exception


ROOT_DIR = Path(__file__).resolve().parents[1]
SQLITE_PATH = ROOT_DIR / "neuroscan.db"


class DatabaseIntegrityError(Exception):
    pass


def mysql_configured() -> bool:
    required = ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"]
    return all(os.getenv(key) for key in required)


def get_database_backend() -> str:
    if mysql_configured() and mysql is not None:
        return "MySQL"
    return "SQLite fallback"


def _mysql_connect(include_database: bool = True):
    if mysql is None:
        raise RuntimeError("mysql-connector-python is not installed.")

    config: dict[str, Any] = {
        "host": os.getenv("MYSQL_HOST"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
    }
    if include_database:
        config["database"] = os.getenv("MYSQL_DATABASE")
    return mysql.connector.connect(**config)


def get_connection():
    if mysql_configured() and mysql is not None:
        return _mysql_connect(include_database=True)
    return sqlite3.connect(SQLITE_PATH)


def init_db() -> None:
    if mysql_configured() and mysql is not None:
        admin_conn = _mysql_connect(include_database=False)
        admin_cursor = admin_conn.cursor()
        admin_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{os.getenv('MYSQL_DATABASE')}`")
        admin_conn.commit()
        admin_cursor.close()
        admin_conn.close()

        conn = _mysql_connect(include_database=True)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(255) PRIMARY KEY,
                password VARCHAR(255) NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                doctor VARCHAR(255),
                name VARCHAR(255),
                age INT,
                tumor_pct DOUBLE,
                stage VARCHAR(255),
                date VARCHAR(32),
                study_type VARCHAR(255),
                tumor_type VARCHAR(255),
                tumor_type_source VARCHAR(255),
                tumor_type_confidence DOUBLE,
                affected_region VARCHAR(255),
                volume_mm3 DOUBLE,
                result_json JSON
            )
            """
        )
        conn.commit()
        cursor.close()
        conn.close()
        return

    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor TEXT,
            name TEXT,
            age INTEGER,
            tumor_pct REAL,
            stage TEXT,
            date TEXT
        )
        """
    )
    existing_columns = {row[1] for row in cursor.execute("PRAGMA table_info(patients)").fetchall()}
    for column_name, column_type in [
        ("study_type", "TEXT"),
        ("tumor_type", "TEXT"),
        ("tumor_type_source", "TEXT"),
        ("tumor_type_confidence", "REAL"),
        ("affected_region", "TEXT"),
        ("volume_mm3", "REAL"),
        ("result_json", "TEXT"),
    ]:
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE patients ADD COLUMN {column_name} {column_type}")

    conn.commit()
    conn.close()


def register_user(username: str, password_hash: str) -> None:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if mysql_configured() and mysql is not None:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password_hash))
        else:
            cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password_hash))
        conn.commit()
    except (sqlite3.IntegrityError, MySQLIntegrityError) as error:
        raise DatabaseIntegrityError(str(error)) from error
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


def authenticate_user(username: str) -> str | None:
    conn = get_connection()
    cursor = conn.cursor()
    if mysql_configured() and mysql is not None:
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    else:
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None


def save_patient_record(doctor: str, patient_name: str, patient_age: int, study_type: str, summary: dict, report_json: str, saved_date: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    values = (
        doctor,
        patient_name,
        int(patient_age),
        float(summary["affected_percent"]),
        summary["tumor_level"],
        saved_date,
        study_type,
        summary["tumor_type"],
        summary["tumor_type_source"],
        summary["tumor_type_confidence"],
        summary["estimated_region"],
        summary["affected_volume_mm3"],
        report_json,
    )

    if mysql_configured() and mysql is not None:
        cursor.execute(
            """
            INSERT INTO patients (
                doctor, name, age, tumor_pct, stage, date, study_type, tumor_type,
                tumor_type_source, tumor_type_confidence, affected_region, volume_mm3, result_json
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            values,
        )
    else:
        cursor.execute(
            """
            INSERT INTO patients (
                doctor, name, age, tumor_pct, stage, date, study_type, tumor_type,
                tumor_type_source, tumor_type_confidence, affected_region, volume_mm3, result_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
    conn.commit()
    cursor.close()
    conn.close()


def load_patient_history(doctor: str) -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT name, age, tumor_pct, stage, study_type, tumor_type, tumor_type_source,
               tumor_type_confidence, affected_region, volume_mm3, date
        FROM patients
        WHERE doctor = {placeholder}
        ORDER BY id DESC
    """
    if mysql_configured() and mysql is not None:
        data_frame = pd.read_sql(query.format(placeholder="%s"), conn, params=(doctor,))
    else:
        data_frame = pd.read_sql_query(query.format(placeholder="?"), conn, params=(doctor,))
    conn.close()
    return data_frame
