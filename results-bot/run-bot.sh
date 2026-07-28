#!/usr/bin/env bash
# تشغيل البوت — للماك ولينكس
cd "$(dirname "$0")"

if [ ! -x venv/bin/python ]; then
    echo "❌ لازم تشغّل ./setup.sh الأول."
    exit 1
fi

exec venv/bin/python bot.py
