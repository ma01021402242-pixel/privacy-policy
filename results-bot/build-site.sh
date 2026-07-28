#!/usr/bin/env bash
# بناء الموقع الثابت في فولدر natiga استعدادًا لرفعه على GitHub Pages
cd "$(dirname "$0")"

if [ ! -x venv/bin/python ]; then
    echo "❌ لازم تشغّل ./setup.sh الأول."
    exit 1
fi

exec venv/bin/python build_static.py --clean "$@"
