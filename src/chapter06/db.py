# ket noi python voi database

# Lop quan ly ket noi va truy van database tu Python

import sqlite3
import os
from dataclasses import dataclass
from typing import Optional


# Duong dan mac dinh den file database
DB_PATH = os.path.join("data", "db", "mlops.db")


@dataclass
class Customer:
    """Anh xa (mapping) 1 hang trong bang customers thanh Python object"""
    id           : int
    name         : str
    age          : int
    income       : float
    credit_score : int
    created_at   : str


@dataclass
class Prediction:
    """Anh xa 1 hang trong bang predictions"""
    id             : int
    application_id : int
    model_version  : str
    approved       : bool
    probability    : float
    latency_ms     : Optional[float]
    predicted_at   : str


class Database:
    """
    Quan ly ket noi SQLite va cung cap cac phuong thuc truy van.
    Dung context manager de dam bao ket noi luon duoc dong.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        """
        Tao ket noi den database.
        row_factory: tra ve dict thay vi tuple, de lay gia tri qua ten cot.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Bat foreign key constraint — SQLite tat mac dinh
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ----------------------------------------------------------
    # Cac phuong thuc lam viec voi bang customers
    # ----------------------------------------------------------

    def get_all_customers(self) -> list[Customer]:
        """Lay toan bo khach hang."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM customers ORDER BY id"
            ).fetchall()
        return [Customer(**dict(row)) for row in rows]

    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Lay 1 khach hang theo id. Tra ve None neu khong tim thay."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM customers WHERE id = ?",
                (customer_id,)   # dung ? thay vi f-string de chong SQL Injection
            ).fetchone()
        return Customer(**dict(row)) if row else None

    def get_high_value_customers(self, min_credit_score: int = 700,
                                  min_income: float = 40_000_000) -> list[Customer]:
        """Lay khach hang tiem nang: diem tin dung va thu nhap cao."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM customers
                WHERE credit_score >= ?
                  AND income >= ?
                ORDER BY credit_score DESC
                """,
                (min_credit_score, min_income)
            ).fetchall()
        return [Customer(**dict(row)) for row in rows]

    def insert_customer(self, name: str, age: int,
                        income: float, credit_score: int) -> int:
        """
        Them khach hang moi. Tra ve id vua tao.
        """
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO customers (name, age, income, credit_score)
                VALUES (?, ?, ?, ?)
                """,
                (name, age, income, credit_score)
            )
            # lastrowid: id cua hang vua chen vao
            return cursor.lastrowid

    # ----------------------------------------------------------
    # Cac phuong thuc lam viec voi bang predictions
    # ----------------------------------------------------------

    def insert_prediction(self, application_id: int, model_version: str,
                          approved: bool, probability: float,
                          latency_ms: float = None) -> int:
        """Luu ket qua du doan vao database."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO predictions
                    (application_id, model_version, approved, probability, latency_ms)
                VALUES (?, ?, ?, ?, ?)
                """,
                (application_id, model_version,
                 int(approved), probability, latency_ms)
            )
            return cursor.lastrowid

    def get_model_performance(self, model_version: str) -> dict:
        """
        Tinh cac chi so hieu suat cua model dua tren du lieu da du doan.
        Dung trong Model Monitoring.
        """
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    model_version,
                    COUNT(*)                                AS total_predictions,
                    SUM(approved)                           AS total_approved,
                    ROUND(AVG(probability), 4)              AS avg_probability,
                    ROUND(AVG(latency_ms), 2)               AS avg_latency_ms,
                    ROUND(100.0 * SUM(approved) / COUNT(*), 2) AS approval_rate
                FROM predictions
                WHERE model_version = ?
                GROUP BY model_version
                """,
                (model_version,)
            ).fetchone()
        return dict(row) if row else {}

    def get_pending_applications(self) -> list[dict]:
        """
        Lay danh sach don dang cho xu ly kem thong tin khach hang.
        Pipeline se chay model du doan cho cac don nay.
        """
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    la.id           AS application_id,
                    c.id            AS customer_id,
                    c.name          AS customer_name,
                    c.age,
                    c.income,
                    c.credit_score,
                    la.loan_amount,
                    la.loan_term,
                    la.purpose
                FROM loan_applications la
                INNER JOIN customers c ON la.customer_id = c.id
                WHERE la.status = 'pending'
                ORDER BY la.applied_at
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def update_application_status(self, application_id: int,
                                   status: str) -> bool:
        """Cap nhat trang thai don sau khi co ket qua du doan."""
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE loan_applications SET status = ? WHERE id = ?",
                (status, application_id)
            )
            # rowcount: so hang bi anh huong, 0 nghia la khong tim thay don
            return cursor.rowcount > 0
