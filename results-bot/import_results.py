#!/usr/bin/env python3
"""استيراد ملف النتيجة إلى قاعدة بيانات SQLite.

أمثلة:
    python import_results.py results.xlsx
    python import_results.py results.csv --db results.db --replace
    python import_results.py results.xlsx --sheet "الشيت الأول" --header-row 3
    python import_results.py results.csv --dry-run
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from resultsbot import config
from resultsbot.readers import ReaderError, read_records
from resultsbot.schema import describe_mapping, detect_fields
from resultsbot.store import ResultsStore, build_row

BATCH_SIZE = 5000
HEADER_SAMPLE = 50


def collect_headers(records: list[dict]) -> list[str]:
    """اتحاد مفاتيح أول عدد من السجلات مع الحفاظ على الترتيب."""
    headers: list[str] = []
    seen: set[str] = set()
    for record in records:
        for key in record:
            if key not in seen:
                seen.add(key)
                headers.append(key)
    return headers


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="استيراد ملف نتيجة الثانوية العامة إلى قاعدة بيانات.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", help="مسار ملف النتيجة (csv/xlsx/xls/json/jsonl/db)")
    parser.add_argument(
        "--db", default=str(config.DB_PATH), help="مسار قاعدة البيانات الناتجة"
    )
    parser.add_argument("--sheet", help="اسم الشيت في ملفات إكسيل")
    parser.add_argument("--table", help="اسم الجدول لو المصدر قاعدة SQLite")
    parser.add_argument(
        "--header-row",
        type=int,
        help="رقم صف العناوين (يبدأ من 1) لو الاكتشاف التلقائي غلط",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="يمسح البيانات القديمة قبل الاستيراد",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="يعرض الأعمدة اللي اتعرف عليها وعيّنة من البيانات من غير ما يكتب حاجة",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="يعرض الأعمدة والعيّنة، وبعدين يسأل قبل ما يستورد",
    )
    return parser.parse_args(argv)


def preview(sample: list[dict], mapping: dict, headers: list[str]) -> None:
    print("\n👀 عيّنة من البيانات:")
    shown = 0
    for record in sample:
        row = build_row(record, mapping, headers)
        if row is None:
            continue
        print(f"   رقم الجلوس: {row[0]} | الاسم: {row[2]} | المجموع: {row[4]}")
        shown += 1
        if shown >= 3:
            break


def main(argv=None) -> int:
    args = parse_args(argv)

    try:
        records = read_records(
            args.file, sheet=args.sheet, table=args.table, header_row=args.header_row
        )
        sample: list[dict] = []
        for record in records:
            sample.append(record)
            if len(sample) >= HEADER_SAMPLE:
                break
    except ReaderError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    if not sample:
        print("❌ الملف مفيهوش أي بيانات.", file=sys.stderr)
        return 1

    headers = collect_headers(sample)
    mapping = detect_fields(headers)

    print(f"📄 الملف: {args.file}")
    print(f"🔎 عدد الأعمدة: {len(headers)}")
    print("🧭 الأعمدة اللي اتعرفت عليها:")
    print(describe_mapping(headers, mapping))

    if "seat_no" not in mapping:
        print(
            "\n❌ مقدرتش ألاقي عمود رقم الجلوس.\n"
            "   تأكد إن اسم العمود فيه كلمة «جلوس»، أو حدّد صف العناوين بـ --header-row.",
            file=sys.stderr,
        )
        return 1

    if args.dry_run:
        preview(sample, mapping, headers)
        print("\n(dry-run — مفيش حاجة اتكتبت)")
        return 0

    if args.confirm:
        preview(sample, mapping, headers)
        print(
            "\n📌 راجع فوق: رقم الجلوس والاسم والمجموع طالعين صح؟"
            "\n   (المواد المفروض تكون تحت «أعمدة إضافية» — ده الطبيعي)"
        )
        try:
            answer = input("\n✅ نستورد؟ اكتب y واضغط Enter: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nاتلغى.")
            return 0
        if answer not in {"y", "yes", "ن", "نعم", "ايوه", "ايوة", "أيوة"}:
            print("اتلغى — مفيش حاجة اتكتبت.")
            return 0
        args.replace = True

    store = ResultsStore(args.db)
    store.init_schema()
    if args.replace:
        store.clear()
        print("🧹 اتمسحت البيانات القديمة.")

    imported = 0
    skipped = 0
    batch: list[tuple] = []

    def flush(connection):
        nonlocal batch
        if batch:
            store.insert_batch(connection, batch)
            connection.commit()
            batch = []

    try:
        with store.connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=OFF")
            for record in _chain(sample, records):
                row = build_row(record, mapping, headers)
                if row is None:
                    skipped += 1
                    continue
                batch.append(row)
                imported += 1
                if len(batch) >= BATCH_SIZE:
                    flush(connection)
                    print(f"   … {imported:,} سجل", end="\r", flush=True)
            flush(connection)
    except ReaderError as exc:
        print(f"\n❌ {exc}", file=sys.stderr)
        return 1

    store.set_meta(
        {
            "source_file": Path(args.file).name,
            "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "row_count": str(imported),
        }
    )

    print(f"\n✅ اتخزّن {imported:,} طالب في {args.db}")
    if skipped:
        print(f"⚠️  اتخطّى {skipped:,} صف من غير رقم جلوس.")
    print(f"📦 إجمالي السجلات في القاعدة: {store.count():,}")
    return 0


def _chain(first, rest):
    yield from first
    yield from rest


if __name__ == "__main__":
    raise SystemExit(main())
