"""إعدادات المشروع — بتتقرا من متغيرات البيئة أو ملف .env."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

try:  # python-dotenv اختياري
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:  # pragma: no cover - يعتمد على البيئة
    pass


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on", "نعم"}


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, "").strip() or default)
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, "").strip() or default)
    except ValueError:
        return default


def _int_list(name: str) -> tuple[int, ...]:
    raw = os.getenv(name, "")
    values = []
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if part.lstrip("-").isdigit():
            values.append(int(part))
    return tuple(values)


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
DB_PATH = Path(os.getenv("DB_PATH", "").strip() or BASE_DIR / "results.db")
ADMIN_IDS = _int_list("ADMIN_IDS")

# المجموع الكلي للثانوية العامة — يُستخدم لحساب النسبة لو مش موجودة في الملف
TOTAL_MAX = _float("TOTAL_MAX", 320.0)

ENABLE_NAME_SEARCH = _bool("ENABLE_NAME_SEARCH", True)
NAME_SEARCH_LIMIT = _int("NAME_SEARCH_LIMIT", 8)

# حد أقصى للطلبات لكل مستخدم خلال نافذة زمنية (بالثواني)
RATE_LIMIT_REQUESTS = _int("RATE_LIMIT_REQUESTS", 20)
RATE_LIMIT_WINDOW = _int("RATE_LIMIT_WINDOW", 60)

WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0").strip()
WEB_PORT = _int("WEB_PORT", 8000)
WEB_TITLE = os.getenv("WEB_TITLE", "نتيجة الثانوية العامة").strip()
