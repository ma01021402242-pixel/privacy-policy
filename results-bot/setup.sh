#!/usr/bin/env bash
# تجهيز المشروع — للماك ولينكس
set -e
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "❌ بايثون مش متسطّب. نزّله من https://www.python.org/downloads/"
    exit 1
fi

"$PY" setup.py
