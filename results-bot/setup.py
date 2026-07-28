#!/usr/bin/env python3
"""تجهيز المشروع بخطوة واحدة: بيئة بايثون + المكتبات + التوكن.

بيتشغّل من setup.bat على ويندوز أو setup.sh على ماك/لينكس، وممكن كمان:
    python setup.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / "venv"
ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE = BASE_DIR / ".env.example"
MIN_PYTHON = (3, 9)

TOKEN_PATTERN = re.compile(r"^\d{6,}:[A-Za-z0-9_-]{30,}$")
YES = {"y", "yes", "ن", "نعم", "أيوة", "ايوه", "ايوة"}


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def fail(message: str) -> None:
    print(f"\n❌ {message}")
    sys.exit(1)


def run(command: list, description: str) -> None:
    result = subprocess.run(command)
    if result.returncode != 0:
        fail(f"{description} فشل. شوف الرسالة اللي فوق دي.")


def check_python() -> None:
    if sys.version_info < MIN_PYTHON:
        fail(
            f"نسخة بايثون عندك {sys.version_info.major}.{sys.version_info.minor}، "
            f"والمطلوب {MIN_PYTHON[0]}.{MIN_PYTHON[1]} أو أحدث.\n"
            "   نزّل نسخة جديدة من https://www.python.org/downloads/"
        )


def create_venv() -> None:
    if venv_python().exists():
        print("✅ بيئة بايثون موجودة بالفعل.")
        return
    print("⏳ [1/3] بنجهّز بيئة بايثون...")
    run([sys.executable, "-m", "venv", str(VENV_DIR)], "إنشاء بيئة بايثون")
    if not venv_python().exists():
        fail("مقدرتش أعمل بيئة بايثون. جرّب تنزّل بايثون تاني من python.org")
    print("✅ اتعملت.")


def install_requirements() -> None:
    print("\n⏳ [2/3] بننزّل المكتبات... (ممكن تاخد دقيقة أو اتنين)")
    python = str(venv_python())
    subprocess.run(
        [python, "-m", "pip", "install", "--upgrade", "pip"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    run(
        [python, "-m", "pip", "install", "-r", str(BASE_DIR / "requirements.txt")],
        "تنزيل المكتبات",
    )
    print("✅ اتنزّلت.")


def read_token() -> str | None:
    print("\n🔑 [3/3] التوكن")
    print("   لو لسه معملتش بوت: افتح @BotFather على تليجرام وابعتله /newbot")
    print("   وهيرد عليك بسطر شكله كده:")
    print("   7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw\n")

    for attempt in range(3):
        try:
            token = input("   الصق التوكن هنا واضغط Enter: ").strip()
        except (EOFError, KeyboardInterrupt):
            return None
        token = token.strip("'\"").strip()
        if not token:
            print("   ⚠️  مكتبتش حاجة، جرّب تاني.")
            continue
        if TOKEN_PATTERN.match(token):
            return token
        print("   ⚠️  الشكل ده مش مطابق لتوكن تليجرام.")
        if attempt < 2:
            print("      اتأكد إنك ناسخ السطر كله بما فيه الأرقام والنقطتين.")
            continue
        answer = input("   تحب نكمّل بيه برضه؟ [y/N]: ").strip().lower()
        if answer in YES:
            return token
    return None


def write_env(token: str) -> None:
    if ENV_EXAMPLE.exists():
        lines = ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
    else:
        lines = ["TELEGRAM_BOT_TOKEN="]

    updated, found = [], False
    for line in lines:
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            updated.append(f"TELEGRAM_BOT_TOKEN={token}")
            found = True
        else:
            updated.append(line)
    if not found:
        updated.insert(0, f"TELEGRAM_BOT_TOKEN={token}")

    ENV_FILE.write_text("\n".join(updated) + "\n", encoding="utf-8")
    print(f"✅ التوكن اتحفظ في {ENV_FILE.name}")


def handle_token() -> bool:
    if ENV_FILE.exists():
        current = ENV_FILE.read_text(encoding="utf-8")
        has_token = any(
            line.startswith("TELEGRAM_BOT_TOKEN=") and line.split("=", 1)[1].strip()
            for line in current.splitlines()
        )
        if has_token:
            print("\n🔑 [3/3] التوكن محفوظ بالفعل.")
            try:
                answer = input("   تحب تغيّره؟ [y/N]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                return True
            if answer not in YES:
                return True

    token = read_token()
    if token is None:
        print("\n⚠️  التوكن اتخطّى. تقدر تحطه بعدين في ملف .env")
        return False
    write_env(token)
    return True


def main() -> int:
    print("=" * 46)
    print("   تجهيز بوت نتيجة الثانوية العامة")
    print("=" * 46)
    print()

    check_python()
    create_venv()
    install_requirements()
    has_token = handle_token()

    database = BASE_DIR / "results.db"
    print("\n" + "=" * 46)
    print("🎉 التجهيز خلص!")
    print("=" * 46)
    print("\nالخطوات الجاية:")

    step = 1
    if not has_token:
        print(f"  {step}. افتح ملف .env وحط التوكن بعد =")
        step += 1
    if not database.exists():
        if os.name == "nt":
            print(f"  {step}. اسحب ملف النتيجة وارميه على ملف import.bat")
        else:
            print(f"  {step}. شغّل:  ./import.sh results.xlsx")
        step += 1
    if os.name == "nt":
        print(f"  {step}. اعمل دبل كليك على run-bot.bat")
    else:
        print(f"  {step}. شغّل:  ./run-bot.sh")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n\nاتلغى.")
        raise SystemExit(130)
