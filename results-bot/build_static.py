#!/usr/bin/env python3
"""بناء نسخة ثابتة من موقع النتيجة تشتغل على GitHub Pages من غير سيرفر.

الفكرة: بدل ما المتصفح ينزّل النتيجة كلها، بنقسّمها لملفات صغيرة حسب آخر
أرقام رقم الجلوس. الطالب لما يدوّر، المتصفح بينزّل ملف واحد صغير بس.

    python build_static.py
    python build_static.py --db results.db --out ../natiga
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

from resultsbot import config
from resultsbot.store import ResultsStore, row_to_dict

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE = BASE_DIR / "static" / "site.html"

# نستهدف من ٥٠٠ لـ ١٥٠٠ سجل في الملف الواحد
SINGLE_FILE_LIMIT = 2000
TWO_DIGIT_LIMIT = 150_000


class Interner:
    """جدول للقيم المتكررة (المدارس، المحافظات...) عشان نصغّر حجم الملفات."""

    def __init__(self):
        self.values: list[str] = []
        self._index: dict[str, int] = {}

    def add(self, value: str) -> int | None:
        if not value:
            return None
        index = self._index.get(value)
        if index is None:
            index = len(self.values)
            self._index[value] = index
            self.values.append(value)
        return index


def shard_digits_for(count: int) -> int:
    if count <= SINGLE_FILE_LIMIT:
        return 0
    if count <= TWO_DIGIT_LIMIT:
        return 2
    return 3


def shard_name(seat: str, digits: int) -> str:
    if digits == 0:
        return "all"
    return seat[-digits:].rjust(digits, "0")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="بناء موقع ثابت للنتيجة يشتغل على GitHub Pages."
    )
    parser.add_argument("--db", default=str(config.DB_PATH), help="قاعدة البيانات")
    parser.add_argument(
        "--out",
        default=str(BASE_DIR.parent / "natiga"),
        help="فولدر الموقع الناتج (الافتراضي: natiga في جذر الريبو)",
    )
    parser.add_argument(
        "--title", default=config.WEB_TITLE, help="عنوان الصفحة"
    )
    parser.add_argument(
        "--clean", action="store_true", help="يمسح الفولدر القديم قبل البناء"
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    store = ResultsStore(args.db)
    if not store.exists():
        print(
            f"❌ قاعدة البيانات مش موجودة: {args.db}\n"
            "   شغّل import.bat (أو ./import.sh) الأول.",
            file=sys.stderr,
        )
        return 1

    count = store.count()
    if not count:
        print("❌ قاعدة البيانات فاضية.", file=sys.stderr)
        return 1

    digits = shard_digits_for(count)
    out_dir = Path(args.out).resolve()
    data_dir = out_dir / "data"

    if args.clean and out_dir.exists():
        shutil.rmtree(out_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 عدد الطلبة: {count:,}")
    print(f"🔪 التقسيم: {'ملف واحد' if not digits else f'آخر {digits} أرقام'}")

    # ---------------------------------------------------- المرور الأول
    print("\n⏳ [1/2] بنجهّز جداول القيم المتكررة...")
    subjects: list[str] = []
    seen_subjects: set[str] = set()
    statuses, schools = Interner(), Interner()
    administrations, governorates, branches = Interner(), Interner(), Interner()

    with store.connect() as connection:
        for row in connection.execute("SELECT * FROM students"):
            record = row_to_dict(row)
            for header in record["extra"]:
                if header not in seen_subjects:
                    seen_subjects.add(header)
                    subjects.append(header)
            statuses.add(record.get("status") or "")
            schools.add(record.get("school") or "")
            administrations.add(record.get("administration") or "")
            governorates.add(record.get("governorate") or "")
            branches.add(record.get("branch") or "")

    print(
        f"   المواد/الأعمدة: {len(subjects)} | المدارس: {len(schools.values):,} | "
        f"المحافظات: {len(governorates.values)}"
    )

    # ---------------------------------------------------- المرور الثاني
    print("\n⏳ [2/2] بنكتب ملفات الموقع...")
    total_max = config.TOTAL_MAX or None
    shard_sizes: Counter[str] = Counter()
    written = 0
    current_name: str | None = None
    current: dict[str, list] = {}

    def flush() -> None:
        nonlocal current, current_name
        if current_name is None:
            return
        path = data_dir / f"{current_name}.json"
        path.write_text(
            json.dumps(current, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        shard_sizes[current_name] = len(current)
        current = {}
        current_name = None

    order = "seat_no" if not digits else f"substr(seat_no, -{digits})"
    with store.connect() as connection:
        for row in connection.execute(f"SELECT * FROM students ORDER BY {order}"):
            record = row_to_dict(row)
            seat = record["seat_no"]
            name = shard_name(seat, digits)
            if name != current_name:
                flush()
                current_name = name

            percentage = record.get("percentage")
            total = record.get("total")
            if percentage is None and total is not None and total_max:
                percentage = round(float(total) / float(total_max) * 100, 2)

            extra = record["extra"]
            current[seat] = [
                record.get("name") or "",
                total,
                percentage,
                statuses.add(record.get("status") or ""),
                schools.add(record.get("school") or ""),
                administrations.add(record.get("administration") or ""),
                governorates.add(record.get("governorate") or ""),
                branches.add(record.get("branch") or ""),
                [extra.get(subject) or None for subject in subjects],
            ]
            written += 1
            if written % 50000 == 0:
                print(f"   … {written:,}", end="\r", flush=True)
        flush()

    meta = store.get_meta()
    (data_dir / "meta.json").write_text(
        json.dumps(
            {
                "version": 1,
                "count": written,
                "shard_digits": digits,
                "total_max": total_max,
                "updated_at": meta.get("imported_at", ""),
                "subjects": subjects,
                "statuses": statuses.values,
                "schools": schools.values,
                "administrations": administrations.values,
                "governorates": governorates.values,
                "branches": branches.values,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )

    page = TEMPLATE.read_text(encoding="utf-8").replace("{{TITLE}}", args.title)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    # بيمنع GitHub Pages من معالجة ملفات البيانات، وده بيسرّع النشر
    (out_dir / ".nojekyll").write_text("", encoding="utf-8")

    size = sum(path.stat().st_size for path in out_dir.rglob("*") if path.is_file())
    biggest = max(shard_sizes.values()) if shard_sizes else 0
    shard_bytes = max(
        (path.stat().st_size for path in data_dir.glob("*.json")), default=0
    )

    print(f"\n\n✅ الموقع اتبنى في: {out_dir}")
    print(f"   • عدد الملفات: {len(shard_sizes):,} ملف بيانات")
    print(f"   • أكبر ملف: {biggest:,} طالب (~{shard_bytes / 1024:.0f} كيلوبايت)")
    print(f"   • الحجم الكلي: {size / 1024 / 1024:.1f} ميجابايت")
    print("\nالخطوة الجاية: ارفع الفولدر ده على الريبو واشغّل GitHub Pages.")
    print("التفاصيل في PAGES-AR.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
