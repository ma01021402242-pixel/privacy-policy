#!/usr/bin/env python3
"""بوت تليجرام للاستعلام عن نتيجة الثانوية العامة برقم الجلوس.

التشغيل:
    export TELEGRAM_BOT_TOKEN="..."   # أو حطّه في ملف .env
    python bot.py
"""

from __future__ import annotations

import logging
import re
import time
from collections import defaultdict, deque

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from resultsbot import config
from resultsbot.arabic import normalize_arabic, to_ascii_digits
from resultsbot.formatting import format_matches, format_result, format_top
from resultsbot.store import ResultsStore

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("results-bot")

store = ResultsStore(config.DB_PATH)

_SEPARATORS = re.compile(r"[\s\-_/\\.,]+")
_recent_requests: dict[int, deque[float]] = defaultdict(deque)

WELCOME = (
    "🎓 أهلاً بيك في بوت نتيجة الثانوية العامة\n\n"
    "ابعتلي *رقم الجلوس* بس وهجيبلك النتيجة كاملة بالدرجات.\n"
    "مثال: 123456\n\n"
    "تقدر كمان تبعت اسم الطالب للبحث بالاسم.\n"
    "/help للمساعدة"
)

HELP = (
    "📖 طريقة الاستخدام:\n\n"
    "• ابعت رقم الجلوس (بالعربي أو الإنجليزي) → تجيلك النتيجة.\n"
    "• ابعت اسم الطالب (كلمتين على الأقل) → تجيلك قائمة بالمطابقات.\n\n"
    "الأوامر:\n"
    "/start — البداية\n"
    "/help — المساعدة\n"
    "/top — الأوائل حسب المجموع\n"
    "/stats — حالة قاعدة البيانات\n"
    "/id — رقم حسابك في تليجرام"
)


def is_rate_limited(user_id: int) -> bool:
    """حد بسيط للطلبات يمنع الإغراق."""
    now = time.monotonic()
    window = _recent_requests[user_id]
    while window and now - window[0] > config.RATE_LIMIT_WINDOW:
        window.popleft()
    if len(window) >= config.RATE_LIMIT_REQUESTS:
        return True
    window.append(now)
    return False


async def cmd_start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME, parse_mode="Markdown")


async def cmd_help(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP)


async def cmd_id(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"رقم حسابك: {update.effective_user.id}")


async def cmd_top(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if is_rate_limited(update.effective_user.id):
        await update.message.reply_text("استنى شوية 🙂 بتبعت طلبات كتير في وقت قصير.")
        return
    if not store.exists():
        await update.message.reply_text("النتيجة لسه مترفعتش على البوت.")
        return
    await update.message.chat.send_action(ChatAction.TYPING)
    await update.message.reply_text(format_top(store.top(10), config.TOTAL_MAX))


async def cmd_stats(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if config.ADMIN_IDS and update.effective_user.id not in config.ADMIN_IDS:
        await update.message.reply_text("الأمر ده للأدمن بس.")
        return
    if not store.exists():
        await update.message.reply_text("قاعدة البيانات لسه مش موجودة.")
        return
    meta = store.get_meta()
    lines = [
        "📊 حالة قاعدة البيانات:",
        f"• عدد الطلبة: {store.count():,}",
        f"• الملف المصدر: {meta.get('source_file', 'غير معروف')}",
        f"• آخر استيراد: {meta.get('imported_at', 'غير معروف')}",
    ]
    await update.message.reply_text("\n".join(lines))


async def on_text(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if message is None or not message.text:
        return

    user_id = update.effective_user.id
    if is_rate_limited(user_id):
        await message.reply_text("استنى شوية 🙂 بتبعت طلبات كتير في وقت قصير.")
        return

    if not store.exists():
        await message.reply_text(
            "النتيجة لسه مترفعتش على البوت. جرّب تاني بعد شوية 🙏"
        )
        return

    text = message.text.strip()
    compact = _SEPARATORS.sub("", to_ascii_digits(text))

    await message.chat.send_action(ChatAction.TYPING)

    if compact.isdigit():
        record = store.get_by_seat(compact)
        if record is None:
            await message.reply_text(
                f"🚫 مفيش نتيجة لرقم الجلوس «{compact}».\n"
                "اتأكد من الرقم، وياريت تبعته من غير مسافات."
            )
            return
        await message.reply_text(format_result(record, config.TOTAL_MAX))
        return

    if not config.ENABLE_NAME_SEARCH:
        await message.reply_text("ابعت رقم الجلوس بالأرقام من فضلك.")
        return

    query = normalize_arabic(text)
    if len(query) < 4 or len(query.split()) < 2:
        await message.reply_text(
            "ابعت رقم الجلوس بالأرقام، أو اكتب اسم الطالب كلمتين على الأقل."
        )
        return

    matches = store.search_by_name(text, config.NAME_SEARCH_LIMIT)
    if len(matches) == 1:
        await message.reply_text(format_result(matches[0], config.TOTAL_MAX))
        return
    await message.reply_text(format_matches(matches, text))


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("خطأ أثناء معالجة التحديث", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        try:
            await update.message.reply_text("حصل خطأ مؤقت، جرّب تاني بعد شوية 🙏")
        except Exception:  # pragma: no cover - أثناء الأعطال الشبكية
            pass


def main() -> None:
    if not config.BOT_TOKEN:
        raise SystemExit(
            "❌ لازم تحط TELEGRAM_BOT_TOKEN في متغيرات البيئة أو في ملف .env"
        )
    if not store.exists():
        logger.warning(
            "قاعدة البيانات %s مش موجودة — شغّل import_results.py الأول.",
            config.DB_PATH,
        )

    application = Application.builder().token(config.BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("id", cmd_id))
    application.add_handler(CommandHandler("top", cmd_top))
    application.add_handler(CommandHandler("stats", cmd_stats))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    application.add_error_handler(on_error)

    logger.info("البوت اشتغل ✅")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
