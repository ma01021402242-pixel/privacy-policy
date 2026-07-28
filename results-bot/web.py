#!/usr/bin/env python3
"""موقع بسيط للاستعلام عن النتيجة برقم الجلوس.

التشغيل للتجربة:
    python web.py
للإنتاج:
    pip install waitress && waitress-serve --port=8000 web:app
"""

from __future__ import annotations

import re
import time
from collections import defaultdict, deque

from flask import Flask, jsonify, request, send_from_directory

from resultsbot import config
from resultsbot.arabic import normalize_arabic, to_ascii_digits
from resultsbot.formatting import compute_percentage, format_result, status_icon
from resultsbot.store import ResultsStore

app = Flask(__name__, static_folder="static", static_url_path="")
store = ResultsStore(config.DB_PATH)

_SEPARATORS = re.compile(r"[\s\-_/\\.,]+")
_hits: dict[str, deque[float]] = defaultdict(deque)


def _rate_limited(key: str) -> bool:
    now = time.monotonic()
    window = _hits[key]
    while window and now - window[0] > config.RATE_LIMIT_WINDOW:
        window.popleft()
    if len(window) >= config.RATE_LIMIT_REQUESTS:
        return True
    window.append(now)
    return False


def _public(record: dict) -> dict:
    """السجل بالشكل اللي الصفحة بتستهلكه."""
    return {
        "seat_no": record["seat_no"],
        "name": record.get("name") or "",
        "status": record.get("status") or "",
        "status_icon": status_icon(record.get("status") or ""),
        "total": record.get("total"),
        "total_max": config.TOTAL_MAX or None,
        "percentage": compute_percentage(record, config.TOTAL_MAX),
        "school": record.get("school") or "",
        "administration": record.get("administration") or "",
        "governorate": record.get("governorate") or "",
        "branch": record.get("branch") or "",
        "subjects": record.get("extra") or {},
        "text": format_result(record, config.TOTAL_MAX),
    }


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/config")
def api_config():
    meta = store.get_meta() if store.exists() else {}
    return jsonify(
        {
            "title": config.WEB_TITLE,
            "ready": store.exists(),
            "name_search": config.ENABLE_NAME_SEARCH,
            "updated_at": meta.get("imported_at", ""),
        }
    )


@app.get("/api/result")
def api_result():
    if _rate_limited(request.remote_addr or "unknown"):
        return jsonify({"error": "طلبات كتير في وقت قصير، استنى شوية."}), 429

    if not store.exists():
        return jsonify({"error": "النتيجة لسه مترفعتش."}), 503

    query = (request.args.get("q") or "").strip()
    if not query:
        return jsonify({"error": "اكتب رقم الجلوس."}), 400

    compact = _SEPARATORS.sub("", to_ascii_digits(query))
    if compact.isdigit():
        record = store.get_by_seat(compact)
        if record is None:
            return jsonify({"error": f"مفيش نتيجة لرقم الجلوس «{compact}»."}), 404
        return jsonify({"result": _public(record)})

    if not config.ENABLE_NAME_SEARCH:
        return jsonify({"error": "البحث بالاسم مقفول — اكتب رقم الجلوس."}), 400

    normalized = normalize_arabic(query)
    if len(normalized) < 4 or len(normalized.split()) < 2:
        return jsonify({"error": "اكتب اسم الطالب كلمتين على الأقل."}), 400

    matches = store.search_by_name(query, config.NAME_SEARCH_LIMIT)
    if not matches:
        return jsonify({"error": f"مفيش نتائج للاسم «{query}»."}), 404
    if len(matches) == 1:
        return jsonify({"result": _public(matches[0])})
    return jsonify(
        {
            "matches": [
                {
                    "seat_no": record["seat_no"],
                    "name": record.get("name") or "",
                    "governorate": record.get("governorate") or "",
                    "school": record.get("school") or "",
                }
                for record in matches
            ]
        }
    )


if __name__ == "__main__":
    app.run(host=config.WEB_HOST, port=config.WEB_PORT)
