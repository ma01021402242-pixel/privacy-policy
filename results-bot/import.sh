#!/usr/bin/env bash
# استيراد ملف النتيجة — للماك ولينكس
#   ./import.sh results.xlsx
cd "$(dirname "$0")"

if [ ! -x venv/bin/python ]; then
    echo "❌ لازم تشغّل ./setup.sh الأول."
    exit 1
fi

if [ -z "$1" ]; then
    echo "الاستخدام:  ./import.sh مسار_ملف_النتيجة"
    echo "مثال:       ./import.sh results.xlsx"
    exit 1
fi

exec venv/bin/python import_results.py "$1" --confirm
