#!/usr/bin/env python3
"""اختبارات سريعة للمنطق الأساسي — مش محتاجة أي مكتبات خارجية.

    python tests.py
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from resultsbot.arabic import digits_only, normalize_arabic, parse_number
from resultsbot.formatting import format_result, status_icon
from resultsbot.readers import read_records
from resultsbot.schema import detect_fields
from resultsbot.store import ResultsStore, build_row, normalize_seat

SAMPLE = Path(__file__).parent / "sample" / "sample_results.csv"


class TestArabic(unittest.TestCase):
    def test_arabic_indic_digits(self):
        self.assertEqual(digits_only("١٢٣٤٥٦"), "123456")
        self.assertEqual(digits_only(" 12-34 "), "1234")

    def test_letter_normalization(self):
        self.assertEqual(normalize_arabic("أحمد"), normalize_arabic("احمد"))
        self.assertEqual(normalize_arabic("منة"), normalize_arabic("منه"))
        self.assertEqual(normalize_arabic("مصطفى"), normalize_arabic("مصطفي"))
        self.assertEqual(normalize_arabic("مُحَمَّد"), normalize_arabic("محمد"))

    def test_parse_number(self):
        self.assertEqual(parse_number("٣١٠"), 310.0)
        self.assertEqual(parse_number("96.88%"), 96.88)
        self.assertEqual(parse_number(275), 275.0)
        self.assertIsNone(parse_number("غ"))
        self.assertIsNone(parse_number(""))
        self.assertIsNone(parse_number(None))


class TestSchema(unittest.TestCase):
    def test_detects_common_headers(self):
        headers = ["رقم الجلوس", "اسم الطالب", "المجموع", "الرأي", "اللغة العربية"]
        mapping = detect_fields(headers)
        self.assertEqual(mapping["seat_no"], 0)
        self.assertEqual(mapping["name"], 1)
        self.assertEqual(mapping["total"], 2)
        self.assertEqual(mapping["status"], 3)
        self.assertNotIn(4, mapping.values())  # المادة تفضل عمود إضافي

    def test_school_not_confused_with_name(self):
        mapping = detect_fields(["اسم المدرسة", "اسم الطالب"])
        self.assertEqual(mapping["school"], 0)
        self.assertEqual(mapping["name"], 1)

    def test_english_headers(self):
        mapping = detect_fields(["Seat Number", "Student Name", "Total"])
        self.assertEqual(mapping["seat_no"], 0)
        self.assertEqual(mapping["name"], 1)
        self.assertEqual(mapping["total"], 2)


class TestStatusIcon(unittest.TestCase):
    def test_icons(self):
        self.assertEqual(status_icon("ناجح"), "✅")
        self.assertEqual(status_icon("دور ثانٍ"), "⚠️")
        self.assertEqual(status_icon("راسب"), "❌")
        self.assertEqual(status_icon(""), "ℹ️")


class TestEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.store = ResultsStore(Path(cls.tmpdir.name) / "test.db")
        cls.store.init_schema()

        records = list(read_records(SAMPLE))
        headers = list(records[0].keys())
        mapping = detect_fields(headers)
        rows = [build_row(record, mapping, headers) for record in records]
        with cls.store.connect() as connection:
            cls.store.insert_batch(connection, [row for row in rows if row])
            connection.commit()

    @classmethod
    def tearDownClass(cls):
        cls.tmpdir.cleanup()

    def test_imported_all_rows(self):
        self.assertEqual(self.store.count(), 5)

    def test_lookup_variants(self):
        for seat in ("100001", "١٠٠٠٠١", "0100001", " 100-001 "):
            with self.subTest(seat=seat):
                record = self.store.get_by_seat(normalize_seat(seat))
                self.assertIsNotNone(record)
                self.assertEqual(record["seat_no"], "100001")

    def test_missing_seat(self):
        self.assertIsNone(self.store.get_by_seat("999999"))

    def test_subjects_kept_as_extra(self):
        record = self.store.get_by_seat("100001")
        self.assertIn("اللغة العربية", record["extra"])
        self.assertEqual(record["extra"]["اللغة العربية"], "72")

    def test_name_search(self):
        matches = self.store.search_by_name("محمد أحمد")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["seat_no"], "100001")

    def test_name_search_ignores_hamza(self):
        self.assertEqual(
            [row["seat_no"] for row in self.store.search_by_name("منه الله خالد")],
            ["100004"],
        )

    def test_format_result(self):
        text = format_result(self.store.get_by_seat("100001"), 320.0)
        self.assertIn("محمد أحمد إبراهيم علي", text)
        self.assertIn("302 من 320", text)
        self.assertIn("94.38%", text)
        self.assertIn("اللغة العربية: 72", text)

    def test_top(self):
        totals = [record["total"] for record in self.store.top(3)]
        self.assertEqual(totals, sorted(totals, reverse=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
