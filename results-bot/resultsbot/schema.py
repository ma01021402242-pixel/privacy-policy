"""التعرّف التلقائي على أعمدة ملف النتيجة.

مش بنفترض شكل معيّن للملف — بنقرأ عناوين الأعمدة ونحاول نطابقها مع أسماء
معروفة. أي عمود مش متعرّف عليه (المواد مثلاً) بيتخزّن زي ما هو في عمود extra.
"""

from __future__ import annotations

from .arabic import normalize_key

CORE_FIELDS = (
    "seat_no",
    "name",
    "total",
    "percentage",
    "status",
    "school",
    "administration",
    "governorate",
    "branch",
)

FIELD_LABELS = {
    "seat_no": "رقم الجلوس",
    "name": "الاسم",
    "total": "المجموع",
    "percentage": "النسبة",
    "status": "الحالة",
    "school": "المدرسة",
    "administration": "الإدارة التعليمية",
    "governorate": "المحافظة",
    "branch": "الشعبة",
}

# مطابقة كاملة لعنوان العمود
ALIASES: dict[str, tuple[str, ...]] = {
    "seat_no": (
        "رقم الجلوس",
        "رقم جلوس",
        "الجلوس",
        "جلوس",
        "رقم الجلوس للطالب",
        "كود الطالب",
        "رقم الطالب",
        "seat",
        "seat no",
        "seat_no",
        "seat number",
        "seatnumber",
        "id",
    ),
    "name": (
        "الاسم",
        "اسم",
        "اسم الطالب",
        "الاسم رباعي",
        "اسم الطالب رباعي",
        "الاسم بالكامل",
        "name",
        "student name",
        "full name",
    ),
    "total": (
        "المجموع",
        "مجموع",
        "مجموع الدرجات",
        "المجموع الكلي",
        "الدرجة الكلية",
        "درجة الطالب",
        "total",
        "total marks",
        "grand total",
    ),
    "percentage": (
        "النسبة",
        "النسبة المئوية",
        "نسبة",
        "المئوية",
        "percent",
        "percentage",
        "ratio",
    ),
    "status": (
        "الحالة",
        "حالة الطالب",
        "الرأي",
        "النتيجة",
        "الموقف",
        "الموقف من النتيجة",
        "status",
        "result",
    ),
    "school": ("المدرسة", "اسم المدرسة", "school", "school name"),
    "administration": (
        "الإدارة",
        "الإدارة التعليمية",
        "ادارة",
        "administration",
        "directorate",
    ),
    "governorate": ("المحافظة", "محافظة", "governorate", "gov"),
    "branch": ("الشعبة", "القسم", "الشعبة الدراسية", "branch", "section", "track"),
}

# مطابقة جزئية (لو العنوان فيه الكلمة دي)
HINTS: dict[str, tuple[str, ...]] = {
    "seat_no": ("جلوس", "seat"),
    "name": ("الاسم", "اسم الطالب", "student name"),
    "total": ("المجموع", "total"),
    "percentage": ("النسبة", "percent"),
    "status": ("الحالة", "النتيجة", "الرأي", "status"),
    "school": ("مدرسة", "school"),
    "administration": ("ادارة", "administration"),
    "governorate": ("محافظة", "governorate"),
    "branch": ("الشعبة", "القسم", "branch"),
}


def detect_fields(headers) -> dict[str, int]:
    """يرجّع خريطة {اسم الحقل: رقم العمود} من عناوين الأعمدة."""
    normalized = [normalize_key(header) for header in headers]
    mapping: dict[str, int] = {}
    used: set[int] = set()

    for stage in (ALIASES, HINTS):
        exact = stage is ALIASES
        for field in CORE_FIELDS:
            if field in mapping:
                continue
            for candidate in stage.get(field, ()):
                needle = normalize_key(candidate)
                if not needle:
                    continue
                for index, header in enumerate(normalized):
                    if index in used or not header:
                        continue
                    matched = header == needle if exact else needle in header
                    if matched:
                        mapping[field] = index
                        used.add(index)
                        break
                if field in mapping:
                    break
    return mapping


def describe_mapping(headers, mapping) -> str:
    """وصف نصي للأعمدة اللي اتعرف عليها — بيتطبع أثناء الاستيراد."""
    lines = []
    for field in CORE_FIELDS:
        index = mapping.get(field)
        label = FIELD_LABELS[field]
        if index is None:
            lines.append(f"  - {label:<18} : (غير موجود)")
        else:
            lines.append(f"  - {label:<18} : عمود «{headers[index]}»")
    extras = [h for i, h in enumerate(headers) if i not in set(mapping.values()) and h]
    if extras:
        preview = "، ".join(extras[:12])
        more = f" ... (+{len(extras) - 12})" if len(extras) > 12 else ""
        lines.append(f"  - أعمدة إضافية ({len(extras)}) : {preview}{more}")
    return "\n".join(lines)
