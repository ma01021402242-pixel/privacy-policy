"""تخزين النتيجة في قاعدة SQLite والبحث فيها."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .arabic import clean_text, digits_only, normalize_arabic, parse_number

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    seat_no        TEXT PRIMARY KEY,
    seat_key       TEXT,
    name           TEXT,
    name_norm      TEXT,
    total          REAL,
    percentage     REAL,
    status         TEXT,
    school         TEXT,
    administration TEXT,
    governorate    TEXT,
    branch         TEXT,
    extra          TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_students_seat_key  ON students(seat_key);
CREATE INDEX IF NOT EXISTS idx_students_name_norm ON students(name_norm);
CREATE INDEX IF NOT EXISTS idx_students_total     ON students(total DESC);

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""

COLUMNS = (
    "seat_no",
    "seat_key",
    "name",
    "name_norm",
    "total",
    "percentage",
    "status",
    "school",
    "administration",
    "governorate",
    "branch",
    "extra",
)

_INSERT = (
    f"INSERT OR REPLACE INTO students ({', '.join(COLUMNS)}) "
    f"VALUES ({', '.join('?' * len(COLUMNS))})"
)


def normalize_seat(value) -> str:
    """رقم الجلوس كما نخزّنه: أرقام إنجليزية فقط."""
    digits = digits_only(value)
    if digits:
        return digits
    return normalize_arabic(value).replace(" ", "")


def build_row(record: dict, mapping: dict[str, int], headers: list[str]) -> tuple | None:
    """يحوّل سجل خام + خريطة الأعمدة لصف جاهز للتخزين."""

    def field(name: str):
        index = mapping.get(name)
        if index is None or index >= len(headers):
            return None
        return record.get(headers[index])

    seat_no = normalize_seat(field("seat_no"))
    if not seat_no:
        return None

    name = clean_text(field("name"))
    total = parse_number(field("total"))
    percentage = parse_number(field("percentage"))

    mapped_headers = {
        headers[index] for index in mapping.values() if index < len(headers)
    }
    extra = {}
    for header, value in record.items():
        if header in mapped_headers:
            continue
        text = clean_text(value)
        if text:
            extra[header] = text

    return (
        seat_no,
        seat_no.lstrip("0") or seat_no,
        name,
        normalize_arabic(name),
        total,
        percentage,
        clean_text(field("status")),
        clean_text(field("school")),
        clean_text(field("administration")),
        clean_text(field("governorate")),
        clean_text(field("branch")),
        json.dumps(extra, ensure_ascii=False),
    )


def row_to_dict(row: sqlite3.Row) -> dict:
    record = dict(row)
    try:
        record["extra"] = json.loads(record.get("extra") or "{}")
    except json.JSONDecodeError:
        record["extra"] = {}
    return record


class ResultsStore:
    """واجهة بسيطة على قاعدة البيانات — كل عملية بتفتح اتصال لوحدها (thread-safe)."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    # ------------------------------------------------------------- الاتصال
    @contextmanager
    def connect(self, readonly: bool = False) -> Iterator[sqlite3.Connection]:
        if readonly and not self.path.exists():
            raise FileNotFoundError(self.path)
        connection = sqlite3.connect(self.path, timeout=15)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()

    def exists(self) -> bool:
        return self.path.exists()

    def init_schema(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA)
            connection.commit()

    # ------------------------------------------------------------ الاستيراد
    def clear(self) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM students")
            connection.commit()

    def insert_batch(self, connection: sqlite3.Connection, rows: list[tuple]) -> None:
        connection.executemany(_INSERT, rows)

    def set_meta(self, values: dict[str, str]) -> None:
        with self.connect() as connection:
            connection.executemany(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                [(key, str(value)) for key, value in values.items()],
            )
            connection.commit()

    def get_meta(self) -> dict[str, str]:
        with self.connect() as connection:
            return {row["key"]: row["value"] for row in connection.execute("SELECT key, value FROM meta")}

    # --------------------------------------------------------------- البحث
    def get_by_seat(self, seat) -> dict | None:
        seat_no = normalize_seat(seat)
        if not seat_no:
            return None
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM students WHERE seat_no = ?", (seat_no,)
            ).fetchone()
            if row is None:
                # نجرب من غير الأصفار البادئة (٠٠١٢٣ = ١٢٣)
                row = connection.execute(
                    "SELECT * FROM students WHERE seat_key = ? LIMIT 1",
                    (seat_no.lstrip("0") or seat_no,),
                ).fetchone()
        return row_to_dict(row) if row else None

    def search_by_name(self, query: str, limit: int = 10) -> list[dict]:
        normalized = normalize_arabic(query)
        tokens = [token for token in normalized.split() if len(token) > 1][:4]
        if not tokens:
            return []

        with self.connect() as connection:
            # المحاولة الأولى: مطابقة من أول الاسم — بتستخدم الفهرس وبترجع فورًا
            rows = connection.execute(
                "SELECT * FROM students WHERE name_norm >= ? AND name_norm < ? "
                "ORDER BY name LIMIT ?",
                (normalized, normalized + "￿", limit),
            ).fetchall()
            if not rows:
                # المحاولة التانية: كل كلمة في أي مكان في الاسم (مسح كامل، أبطأ)
                where = " AND ".join(["name_norm LIKE ?"] * len(tokens))
                params = [f"%{token}%" for token in tokens] + [limit]
                rows = connection.execute(
                    f"SELECT * FROM students WHERE {where} ORDER BY name LIMIT ?",
                    params,
                ).fetchall()
        return [row_to_dict(row) for row in rows]

    def count(self) -> int:
        with self.connect() as connection:
            return connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]

    def top(self, limit: int = 10) -> list[dict]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM students WHERE total IS NOT NULL "
                "ORDER BY total DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [row_to_dict(row) for row in rows]
