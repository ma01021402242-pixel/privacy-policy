"""تطبيع النصوص والأرقام العربية.

ملفات النتيجة بتيجي بأشكال مختلفة: أرقام هندية (٠١٢)، همزات متنوعة، تشكيل،
مسافات زيادة... الدوال دي بتوحّد كل ده عشان المقارنة والبحث يشتغلوا صح.
"""

from __future__ import annotations

import re

_ARABIC_INDIC = "٠١٢٣٤٥٦٧٨٩"
_EXTENDED_ARABIC_INDIC = "۰۱۲۳۴۵۶۷۸۹"

_DIGIT_TRANS: dict[int, str] = {}
for _index, _char in enumerate(_ARABIC_INDIC):
    _DIGIT_TRANS[ord(_char)] = str(_index)
for _index, _char in enumerate(_EXTENDED_ARABIC_INDIC):
    _DIGIT_TRANS[ord(_char)] = str(_index)

# تشكيل + تطويل
_DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
_NON_WORD = re.compile(r"[^0-9a-zء-ي ]+")
_SPACES = re.compile(r"\s+")
_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


def to_ascii_digits(text) -> str:
    """يحوّل الأرقام الهندية/الفارسية لأرقام إنجليزية."""
    if text is None:
        return ""
    return str(text).translate(_DIGIT_TRANS)


def normalize_arabic(text) -> str:
    """يوحّد الحروف ويشيل التشكيل والرموز، ويرجّع نص للمقارنة."""
    if text is None:
        return ""
    value = to_ascii_digits(text).strip().lower()
    value = _DIACRITICS.sub("", value)
    value = value.replace("أ", "ا")  # أ
    value = value.replace("إ", "ا")  # إ
    value = value.replace("آ", "ا")  # آ
    value = value.replace("ى", "ي")  # ى
    value = value.replace("ة", "ه")  # ة
    value = value.replace("ؤ", "و")  # ؤ
    value = value.replace("ئ", "ي")  # ئ
    value = _NON_WORD.sub(" ", value)
    return _SPACES.sub(" ", value).strip()


def normalize_key(text) -> str:
    """نسخة من normalize_arabic من غير مسافات — بتُستخدم لمطابقة عناوين الأعمدة."""
    return normalize_arabic(text).replace(" ", "")


def digits_only(text) -> str:
    """يرجّع الأرقام بس من أي نص (بعد تحويل الأرقام الهندية)."""
    return re.sub(r"\D", "", to_ascii_digits(text))


def parse_number(value):
    """يحوّل أي قيمة لرقم عشري، ويرجّع None لو مش رقم (زي 'غ' أو '-')."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = to_ascii_digits(value).strip()
    if not text:
        return None
    text = text.replace("٫", ".").replace("٬", "").replace(",", "")
    match = _NUMBER.search(text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def clean_text(value) -> str:
    """ينضّف قيمة نصية جاية من الملف من غير ما يغيّر شكلها للمستخدم."""
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return _SPACES.sub(" ", str(value)).strip()
