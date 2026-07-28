"""تنسيق النتيجة كنص جاهز للعرض في تليجرام."""

from __future__ import annotations

from .arabic import normalize_arabic

TELEGRAM_LIMIT = 3900

_STATUS_ICONS = (
    (("ناجح", "نجح", "مقبول", "ناجحة"), "✅"),
    (("دور ثان", "الدور الثاني", "ملحق", "اعادة", "إعادة", "له دور"), "⚠️"),
    (("راسب", "غائب", "محروم", "ملغاة", "ملغى", "موقوف"), "❌"),
)


def status_icon(status: str) -> str:
    normalized = normalize_arabic(status)
    if not normalized:
        return "ℹ️"
    for keywords, icon in _STATUS_ICONS:
        for keyword in keywords:
            if normalize_arabic(keyword) in normalized:
                return icon
    return "ℹ️"


def _format_number(value) -> str:
    if value is None:
        return ""
    if float(value).is_integer():
        return str(int(value))
    return f"{float(value):.2f}".rstrip("0").rstrip(".")


def compute_percentage(record: dict, total_max: float | None) -> float | None:
    percentage = record.get("percentage")
    if percentage is not None:
        return float(percentage)
    total = record.get("total")
    if total is not None and total_max:
        return round(float(total) / float(total_max) * 100, 2)
    return None


def format_result(record: dict, total_max: float | None = None) -> str:
    """كارت النتيجة الكامل."""
    lines = ["🎓 نتيجة الثانوية العامة", "━━━━━━━━━━━━━━━━━━━━"]

    if record.get("name"):
        lines.append(f"👤 الاسم: {record['name']}")
    lines.append(f"🔢 رقم الجلوس: {record['seat_no']}")

    status = record.get("status")
    if status:
        lines.append(f"{status_icon(status)} الحالة: {status}")

    total = record.get("total")
    if total is not None:
        suffix = f" من {_format_number(total_max)}" if total_max else ""
        lines.append(f"📊 المجموع: {_format_number(total)}{suffix}")

    percentage = compute_percentage(record, total_max)
    if percentage is not None:
        lines.append(f"📈 النسبة: {_format_number(percentage)}%")

    for key, label, icon in (
        ("branch", "الشعبة", "📚"),
        ("school", "المدرسة", "🏫"),
        ("administration", "الإدارة", "🏛"),
        ("governorate", "المحافظة", "📍"),
    ):
        if record.get(key):
            lines.append(f"{icon} {label}: {record[key]}")

    extra = record.get("extra") or {}
    if extra:
        lines.append("")
        lines.append("📝 الدرجات:")
        for header, value in extra.items():
            lines.append(f"  • {header}: {value}")

    text = "\n".join(lines)
    if len(text) > TELEGRAM_LIMIT:
        text = text[: TELEGRAM_LIMIT - 20].rstrip() + "\n… (تم الاختصار)"
    return text


def format_top(records: list[dict], total_max: float | None = None) -> str:
    """قائمة أوائل الجمهورية حسب المجموع."""
    if not records:
        return "مفيش بيانات مجاميع في الملف عشان أطلع منها الأوائل."

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    lines = ["🏆 الأوائل حسب المجموع", "━━━━━━━━━━━━━━━━━━━━"]
    for rank, record in enumerate(records, start=1):
        percentage = compute_percentage(record, total_max)
        share = f" ({_format_number(percentage)}%)" if percentage is not None else ""
        name = record.get("name") or f"جلوس {record['seat_no']}"
        lines.append(
            f"{medals.get(rank, f'{rank}.')} {name} — "
            f"{_format_number(record.get('total'))}{share}"
        )
        if record.get("governorate"):
            lines.append(f"     {record['governorate']}")
    return "\n".join(lines)


def format_matches(records: list[dict], query: str) -> str:
    """قائمة نتائج البحث بالاسم."""
    if not records:
        return (
            f"مفيش نتائج للاسم «{query}».\n"
            "جرّب تكتب الاسم بشكل أوضح، أو ابعت رقم الجلوس مباشرةً."
        )

    lines = [f"🔎 لقيت {len(records)} نتيجة مطابقة:", ""]
    for index, record in enumerate(records, start=1):
        name = record.get("name") or "(بدون اسم)"
        seat = record["seat_no"]
        details = []
        if record.get("governorate"):
            details.append(record["governorate"])
        if record.get("school"):
            details.append(record["school"])
        suffix = f" — {' / '.join(details)}" if details else ""
        lines.append(f"{index}. {name}{suffix}")
        lines.append(f"   رقم الجلوس: {seat}")
    lines.append("")
    lines.append("ابعت رقم الجلوس بتاع اللي انت عايزه عشان تشوف النتيجة كاملة.")

    text = "\n".join(lines)
    if len(text) > TELEGRAM_LIMIT:
        text = text[: TELEGRAM_LIMIT - 20].rstrip() + "\n… (تم الاختصار)"
    return text
