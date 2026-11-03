os
import
json
import uuid
import logging
from pathlib import Path
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = Path("users.json")

MENU = [
    ["💰 موجودی واقعی", "💳 واریز واقعی"],
    ["💸 برداشت واقعی", "📋 وضعیت درخواست‌ها"],
]

def load_data():
    if not DATA_FILE.exists():
        return {"users": {}, "requests": {}}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logging.exception("خطا در خواندن داده‌ها")
        return {"users": {}, "requests": {}}

def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    uid = str(update.effective_user.id)

    data["users"].setdefault(uid, {
        "name": update.effective_user.first_name or "کاربر",
        "real_balance_toman": 0
    })
    save_data(data)

    await update.message.reply_text(
        "👑 به GOLD MIKR خوش آمدی!\n\n"
        "💳 واریز واقعی ریالی\n"
        "💸 درخواست برداشت واقعی ریالی\n\n"
        "⚠️ پرداخت واقعی فقط پس از اتصال امن درگاه فعال می‌شود.",
        reply_markup=ReplyKeyboardMarkup(MENU, resize_keyboard=True)
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    data = load_data()

    if uid not in data["users"]:
        await start(update, context)
        return

    if text == "💰 موجودی واقعی":
        balance = data["users"][uid]["real_balance_toman"]
        await update.message.reply_text(
            f"💰 موجودی واقعی تأییدشده: {balance:,} تومان"
        )

    elif text == "💳 واریز واقعی":
        context.user_data["action"] = "deposit_amount"
        await update.message.reply_text(
            "مبلغ واریز را به تومان وارد کن (عدد صحیح و مثبت).\n"
            "فعلاً هیچ پولی ارسال نکن؛ درگاه پرداخت هنوز متصل نیست."
        )

    elif text == "💸 برداشت واقعی":
        context.user_data["action"] = "withdraw_amount"
        await update.message.reply_text(
            "مبلغ درخواستی برداشت را به تومان وارد کن.\n"
            "پرداخت فقط پس از اتصال امن سامانه و تأیید موجودی امکان‌پذیر است."
        )

    elif text == "📋 وضعیت درخواست‌ها":
        requests = [
            r for r in data["requests"].values()
            if r["user_id"] == uid
        ]
        if not requests:
            await update.message.reply_text("هنوز درخواستی ثبت نکرده‌ای.")
        else:
            lines = [
                f"{r['type']} | {r['amount']:,} تومان | {r['status']}"
                for r in requests
            ]
            await update.message.reply_text("\n".join(lines))

    elif context.user_data.get("action") in ("deposit_amount", "withdraw_amount"):
        action = context.user_data.pop("action")
        try:
            amount = int(text.replace(",", "").replace("٬", "").strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("لطفاً یک عدد صحیح و مثبت وارد کن.")
            return

        request_id = str(uuid.uuid4())[:8]
        request_type = "واریز" if action == "deposit_amount" else "برداشت"

        if action == "withdraw_amount":
            balance = data["users"][uid]["real_balance_toman"]
            if amount > balance:
                await update.message.reply_text(
                    "مبلغ درخواست از موجودی واقعی تأییدشده بیشتر است."
                )
                return

        data["requests"][request_id] = {
            "user_id": uid,
            "type": request_type,
            "amount": amount,
            "status": "در انتظار اتصال و تأیید سامانه پرداخت"
        }
        save_data(data)

        await update.message.reply_text(
            f"✅ درخواست {request_type} ثبت شد.\n"
            f"شماره پیگیری: {request_id}\n"
            f"مبلغ: {amount:,} تومان\n\n"
            "این ثبت درخواست به معنی دریافت یا پرداخت پول نیست؛ "
            "درگاه واقعی هنوز متصل نشده است."
        )

    else:
        await update.message.reply_text("یکی از دکمه‌های منو را انتخاب کن.")

def main():
    if not TOKEN:
        raise RuntimeError("متغیر امن BOT_TOKEN تنظیم نشده است.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
os
import
json
import uuid
import logging
from pathlib import Path
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = Path("users.json")

MENU = [
    ["💰 موجودی واقعی", "💳 واریز واقعی"],
    ["💸 برداشت واقعی", "📋 وضعیت درخواست‌ها"],
]

def load_data():
    if not DATA_FILE.exists():
        return {"users": {}, "requests": {}}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logging.exception("خطا در خواندن داده‌ها")
        return {"users": {}, "requests": {}}

def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    uid = str(update.effective_user.id)

    data["users"].setdefault(uid, {
        "name": update.effective_user.first_name or "کاربر",
        "real_balance_toman": 0
    })
    save_data(data)

    await update.message.reply_text(
        "👑 به GOLD MIKR خوش آمدی!\n\n"
        "💳 واریز واقعی ریالی\n"
        "💸 درخواست برداشت واقعی ریالی\n\n"
        "⚠️ پرداخت واقعی فقط پس از اتصال امن درگاه فعال می‌شود.",
        reply_markup=ReplyKeyboardMarkup(MENU, resize_keyboard=True)
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    data = load_data()

    if uid not in data["users"]:
        await start(update, context)
        return

    if text == "💰 موجودی واقعی":
        balance = data["users"][uid]["real_balance_toman"]
        await update.message.reply_text(
            f"💰 موجودی واقعی تأییدشده: {balance:,} تومان"
        )

    elif text == "💳 واریز واقعی":
        context.user_data["action"] = "deposit_amount"
        await update.message.reply_text(
            "مبلغ واریز را به تومان وارد کن (عدد صحیح و مثبت).\n"
            "فعلاً هیچ پولی ارسال نکن؛ درگاه پرداخت هنوز متصل نیست."
        )

    elif text == "💸 برداشت واقعی":
        context.user_data["action"] = "withdraw_amount"
        await update.message.reply_text(
            "مبلغ درخواستی برداشت را به تومان وارد کن.\n"
            "پرداخت فقط پس از اتصال امن سامانه و تأیید موجودی امکان‌پذیر است."
        )

    elif text == "📋 وضعیت درخواست‌ها":
        requests = [
            r for r in data["requests"].values()
            if r["user_id"] == uid
        ]
        if not requests:
            await update.message.reply_text("هنوز درخواستی ثبت نکرده‌ای.")
        else:
            lines = [
                f"{r['type']} | {r['amount']:,} تومان | {r['status']}"
                for r in requests
            ]
            await update.message.reply_text("\n".join(lines))

    elif context.user_data.get("action") in ("deposit_amount", "withdraw_amount"):
        action = context.user_data.pop("action")
        try:
            amount = int(text.replace(",", "").replace("٬", "").strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("لطفاً یک عدد صحیح و مثبت وارد کن.")
            return

        request_id = str(uuid.uuid4())[:8]
        request_type = "واریز" if action == "deposit_amount" else "برداشت"

        if action == "withdraw_amount":
            balance = data["users"][uid]["real_balance_toman"]
            if amount > balance:
                await update.message.reply_text(
                    "مبلغ درخواست از موجودی واقعی تأییدشده بیشتر است."
                )
                return

        data["requests"][request_id] = {
            "user_id": uid,
            "type": request_type,
            "amount": amount,
            "status": "در انتظار اتصال و تأیید سامانه پرداخت"
        }
        save_data(data)

        await update.message.reply_text(
            f"✅ درخواست {request_type} ثبت شد.\n"
            f"شماره پیگیری: {request_id}\n"
            f"مبلغ: {amount:,} تومان\n\n"
            "این ثبت درخواست به معنی دریافت یا پرداخت پول نیست؛ "
            "درگاه واقعی هنوز متصل نشده است."
        )

    else:
        await update.message.reply_text("یکی از دکمه‌های منو را انتخاب کن.")

def main():
    if not TOKEN:
        raise RuntimeError("متغیر امن BOT_TOKEN تنظیم نشده است.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
os
import
json
import uuid
import logging
from pathlib import Path
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = Path("users.json")

MENU = [
    ["💰 موجودی واقعی", "💳 واریز واقعی"],
    ["💸 برداشت واقعی", "📋 وضعیت درخواست‌ها"],
]

def load_data():
    if not DATA_FILE.exists():
        return {"users": {}, "requests": {}}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logging.exception("خطا در خواندن داده‌ها")
        return {"users": {}, "requests": {}}

def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    uid = str(update.effective_user.id)

    data["users"].setdefault(uid, {
        "name": update.effective_user.first_name or "کاربر",
        "real_balance_toman": 0
    })
    save_data(data)

    await update.message.reply_text(
        "👑 به GOLD MIKR خوش آمدی!\n\n"
        "💳 واریز واقعی ریالی\n"
        "💸 درخواست برداشت واقعی ریالی\n\n"
        "⚠️ پرداخت واقعی فقط پس از اتصال امن درگاه فعال می‌شود.",
        reply_markup=ReplyKeyboardMarkup(MENU, resize_keyboard=True)
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    data = load_data()

    if uid not in data["users"]:
        await start(update, context)
        return

    if text == "💰 موجودی واقعی":
        balance = data["users"][uid]["real_balance_toman"]
        await update.message.reply_text(
            f"💰 موجودی واقعی تأییدشده: {balance:,} تومان"
        )

    elif text == "💳 واریز واقعی":
        context.user_data["action"] = "deposit_amount"
        await update.message.reply_text(
            "مبلغ واریز را به تومان وارد کن (عدد صحیح و مثبت).\n"
            "فعلاً هیچ پولی ارسال نکن؛ درگاه پرداخت هنوز متصل نیست."
        )

    elif text == "💸 برداشت واقعی":
        context.user_data["action"] = "withdraw_amount"
        await update.message.reply_text(
            "مبلغ درخواستی برداشت را به تومان وارد کن.\n"
            "پرداخت فقط پس از اتصال امن سامانه و تأیید موجودی امکان‌پذیر است."
        )

    elif text == "📋 وضعیت درخواست‌ها":
        requests = [
            r for r in data["requests"].values()
            if r["user_id"] == uid
        ]
        if not requests:
            await update.message.reply_text("هنوز درخواستی ثبت نکرده‌ای.")
        else:
            lines = [
                f"{r['type']} | {r['amount']:,} تومان | {r['status']}"
                for r in requests
            ]
            await update.message.reply_text("\n".join(lines))

    elif context.user_data.get("action") in ("deposit_amount", "withdraw_amount"):
        action = context.user_data.pop("action")
        try:
            amount = int(text.replace(",", "").replace("٬", "").strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("لطفاً یک عدد صحیح و مثبت وارد کن.")
            return

        request_id = str(uuid.uuid4())[:8]
        request_type = "واریز" if action == "deposit_amount" else "برداشت"

        if action == "withdraw_amount":
            balance = data["users"][uid]["real_balance_toman"]
            if amount > balance:
                await update.message.reply_text(
                    "مبلغ درخواست از موجودی واقعی تأییدشده بیشتر است."
                )
                return

        data["requests"][request_id] = {
            "user_id": uid,
            "type": request_type,
            "amount": amount,
            "status": "در انتظار اتصال و تأیید سامانه پرداخت"
        }
        save_data(data)

        await update.message.reply_text(
            f"✅ درخواست {request_type} ثبت شد.\n"
            f"شماره پیگیری: {request_id}\n"
            f"مبلغ: {amount:,} تومان\n\n"
            "این ثبت درخواست به معنی دریافت یا پرداخت پول نیست؛ "
            "درگاه واقعی هنوز متصل نشده است."
        )

    else:
        await update.message.reply_text("یکی از دکمه‌های منو را انتخاب کن.")

def main():
    if not TOKEN:
        raise RuntimeError("متغیر امن BOT_TOKEN تنظیم نشده است.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
os
import
json
import uuid
import logging
from pathlib import Path
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = Path("users.json")

MENU = [
    ["💰 موجودی واقعی", "💳 واریز واقعی"],
    ["💸 برداشت واقعی", "📋 وضعیت درخواست‌ها"],
]

def load_data():
    if not DATA_FILE.exists():
        return {"users": {}, "requests": {}}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logging.exception("خطا در خواندن داده‌ها")
        return {"users": {}, "requests": {}}

def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    uid = str(update.effective_user.id)

    data["users"].setdefault(uid, {
        "name": update.effective_user.first_name or "کاربر",
        "real_balance_toman": 0
    })
    save_data(data)

    await update.message.reply_text(
        "👑 به GOLD MIKR خوش آمدی!\n\n"
        "💳 واریز واقعی ریالی\n"
        "💸 درخواست برداشت واقعی ریالی\n\n"
        "⚠️ پرداخت واقعی فقط پس از اتصال امن درگاه فعال می‌شود.",
        reply_markup=ReplyKeyboardMarkup(MENU, resize_keyboard=True)
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    data = load_data()

    if uid not in data["users"]:
        await start(update, context)
        return

    if text == "💰 موجودی واقعی":
        balance = data["users"][uid]["real_balance_toman"]
        await update.message.reply_text(
            f"💰 موجودی واقعی تأییدشده: {balance:,} تومان"
        )

    elif text == "💳 واریز واقعی":
        context.user_data["action"] = "deposit_amount"
        await update.message.reply_text(
            "مبلغ واریز را به تومان وارد کن (عدد صحیح و مثبت).\n"
            "فعلاً هیچ پولی ارسال نکن؛ درگاه پرداخت هنوز متصل نیست."
        )

    elif text == "💸 برداشت واقعی":
        context.user_data["action"] = "withdraw_amount"
        await update.message.reply_text(
            "مبلغ درخواستی برداشت را به تومان وارد کن.\n"
            "پرداخت فقط پس از اتصال امن سامانه و تأیید موجودی امکان‌پذیر است."
        )

    elif text == "📋 وضعیت درخواست‌ها":
        requests = [
            r for r in data["requests"].values()
            if r["user_id"] == uid
        ]
        if not requests:
            await update.message.reply_text("هنوز درخواستی ثبت نکرده‌ای.")
        else:
            lines = [
                f"{r['type']} | {r['amount']:,} تومان | {r['status']}"
                for r in requests
            ]
            await update.message.reply_text("\n".join(lines))

    elif context.user_data.get("action") in ("deposit_amount", "withdraw_amount"):
        action = context.user_data.pop("action")
        try:
            amount = int(text.replace(",", "").replace("٬", "").strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("لطفاً یک عدد صحیح و مثبت وارد کن.")
            return

        request_id = str(uuid.uuid4())[:8]
        request_type = "واریز" if action == "deposit_amount" else "برداشت"

        if action == "withdraw_amount":
            balance = data["users"][uid]["real_balance_toman"]
            if amount > balance:
                await update.message.reply_text(
                    "مبلغ درخواست از موجودی واقعی تأییدشده بیشتر است."
                )
                return

        data["requests"][request_id] = {
            "user_id": uid,
            "type": request_type,
            "amount": amount,
            "status": "در انتظار اتصال و تأیید سامانه پرداخت"
        }
        save_data(data)

        await update.message.reply_text(
            f"✅ درخواست {request_type} ثبت شد.\n"
            f"شماره پیگیری: {request_id}\n"
            f"مبلغ: {amount:,} تومان\n\n"
            "این ثبت درخواست به معنی دریافت یا پرداخت پول نیست؛ "
            "درگاه واقعی هنوز متصل نشده است."
        )

    else:
        await update.message.reply_text("یکی از دکمه‌های منو را انتخاب کن.")

def main():
    if not TOKEN:
        raise RuntimeError("متغیر امن BOT_TOKEN تنظیم نشده است.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
