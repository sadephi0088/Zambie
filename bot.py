# -*- coding: utf-8 -*-
import asyncio
import random
import time
from typing import Dict, List

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ===== تنظیمات (با توکن و آیدی تو) =====
CONFIG = {
    "token": "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs",  # توکن
    "owner_id": 7341748124,  # آیدی عددی
    "use_webhook": False,    # این نسخه روی polling اجرا می‌شود
}

# ===== پیام‌ها و لحن =====
def sig(msg: str) -> str:
    return f"{msg} :|"

def warm(msg: str) -> str:
    return f"{msg} ⚜️"

lines = {
    "welcome": lambda name: sig(f"نامت ثبت شد {name}. آرام قدم بردار؛ اینجا قانون تنفس می‌کشد."),
    "soft_warn": sig("کلمه‌هایت زیاد شد. سه گام عقب بنشین."),
    "mute_edict": sig("سکوت تا سپیده. وقتی بازگشتی، کمتر فریاد بزن."),
    "loyal": warm("اشاره کنی، انجام می‌شود. بقیه فقط می‌بینند."),
    "summon_owner": warm("حاضرم. فرمان بده."),
    "summon_other": sig("در سکوت بایست. من بیدارم."),
    "oath": sig("این‌جا قانون تنفس می‌کشد. می‌پذیری؟"),
    "oath_accepted": sig("پذیرفته شد. قانون حافظ توست، نه زنجیرت."),
    "edict_header": sig("حکم صادر شد."),
}

# ===== حالت‌ها و وضعیت هر چت =====
MODES = ["warden", "vow", "edict"]
chat_state: Dict[int, Dict] = {}  # chat_id -> { mode: str }

def ensure_chat(cid: int) -> Dict:
    if cid not in chat_state:
        chat_state[cid] = {"mode": "warden"}
    return chat_state[cid]

def get_mode(cid: int) -> str:
    return ensure_chat(cid)["mode"]

def set_mode(cid: int, mode: str) -> None:
    if mode not in MODES:
        raise ValueError("invalid mode")
    ensure_chat(cid)["mode"] = mode

# ===== ضداسپم ساده =====
user_msgs: Dict[int, List[float]] = {}  # user_id -> timestamps
chat_msgs: Dict[int, List[float]] = {}  # chat_id -> timestamps

USER_POINTS = 6
USER_WINDOW = 8.0
CHAT_POINTS = 60
CHAT_WINDOW = 10.0

def _within_window(times: List[float], window: float) -> List[float]:
    now = time.time()
    return [t for t in times if now - t < window]

async def rate_guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """True = اجازه عبور؛ False = مسدود شد و پاسخ داده شد."""
    if update.effective_user is None or update.effective_chat is None:
        return True

    uid = update.effective_user.id
    cid = update.effective_chat.id
    now = time.time()

    # per-user
    lst_u = user_msgs.get(uid, [])
    lst_u = _within_window(lst_u, USER_WINDOW)
    lst_u.append(now)
    user_msgs[uid] = lst_u
    if len(lst_u) > USER_POINTS:
        try:
            await update.effective_chat.send_message(lines["soft_warn"])
            # تلاش برای حذف پیام (اگر ربات ادمین باشد)
            if update.effective_message:
                await context.bot.delete_message(chat_id=cid, message_id=update.effective_message.message_id)
        except Exception:
            pass
        return False

    # per-chat
    lst_c = chat_msgs.get(cid, [])
    lst_c = _within_window(lst_c, CHAT_WINDOW)
    lst_c.append(now)
    chat_msgs[cid] = lst_c
    if len(lst_c) > CHAT_POINTS:
        try:
            await update.effective_chat.send_message(sig("آرام‌تر. نفس بگیر."))
            if update.effective_message:
                await context.bot.delete_message(chat_id=cid, message_id=update.effective_message.message_id)
        except Exception:
            pass
        return False

    return True

# ===== هندلرها =====
async def on_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await rate_guard(update, context):
        return
    name = update.effective_user.first_name if update.effective_user else "مسافر"
    await update.effective_chat.send_message(lines["welcome"](name))

async def on_summon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await rate_guard(update, context):
        return
    is_owner = (update.effective_user and update.effective_user.id == CONFIG["owner_id"])
    await update.effective_chat.send_message(lines["summon_owner"] if is_owner else lines["summon_other"])

async def on_oath(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await rate_guard(update, context):
        return
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("می‌پذیرم", callback_data="oath_accept")]])
    await update.effective_chat.send_message(lines["oath"], reply_markup=kb)

async def on_oath_accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.callback_query.answer("پذیرفته شد")
        await update.callback_query.edit_message_text(lines["oath_accepted"])
    except Exception:
        pass

async def on_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await rate_guard(update, context):
        return
    cid = update.effective_chat.id
    args = context.args if context.args else []
    if not args:
        # نمایش دکمه‌ها
        buttons = [
            [InlineKeyboardButton(m.upper(), callback_data=f"mode_{m}")]
            for m in MODES
        ]
        await update.effective_chat.send_message(
            sig(f"حالت جاری: {get_mode(cid)}. یکی را انتخاب کن:"),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return
    mode = args[0].strip().lower()
    try:
        set_mode(cid, mode)
        await update.effective_chat.send_message(sig(f"حالت به {mode.upper()} تغییر کرد."))
    except ValueError:
        await update.effective_chat.send_message(sig(f"حالت نامعتبر. گزینه‌ها: {', '.join(MODES)}"))

async def on_mode_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        if not query or not query.data:
            return
        if not query.message:
            return
        cid = query.message.chat_id
        if query.data.startswith("mode_"):
            mode = query.data.split("_", 1)[1]
            set_mode(cid, mode)
            await query.edit_message_text(sig(f"حالت به {mode.upper()} تغییر کرد."))
    except Exception:
        pass

async def on_edict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await rate_guard(update, context):
        return
    cid = update.effective_chat.id
    mode = get_mode(cid)
    if mode != "edict":
        await update.effective_chat.send_message(sig("در این حالت، حکم خاموش است."))
        return
    text = " ".join(context.args) if context.args else "بدون شرح."
    await update.effective_chat.send_message(f"{lines['edict_header']}\n— {text}")

async def on_veil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await rate_guard(update, context):
        return
    msg = update.effective_message
    if not msg or not msg.reply_to_message:
        await update.effective_chat.send_message(sig("روی پیام هدف ریپلای کن و /veil بزن."))
        return
    target = msg.reply_to_message.from_user
    if not target:
        await update.effective_chat.send_message(sig("هدف نامشخص است."))
        return
    try:
        perms = ChatPermissions(can_send_messages=False)
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target.id,
            permissions=perms,
        )
        await update.effective_chat.send_message(lines["mute_edict"])
    except Exception:
        await update.effective_chat.send_message(sig("اجازهٔ کافی برای سکوت ندارم."))

async def on_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await rate_guard(update, context):
        return
    cid = update.effective_chat.id
    await update.effective_chat.send_message(sig(f"mode={get_mode(cid)}"))

async def on_message_tone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # لحن گرم برای مالک به‌صورت تصادفی
    if update.effective_user and update.effective_user.id == CONFIG["owner_id"]:
        if random.random() < 0.02:
            try:
                await update.effective_chat.send_message(warm("دیدم. به چشم."))
            except Exception:
                pass

# ===== اجرای اپلیکیشن =====
async def main():
    app = (
        ApplicationBuilder()
        .token(CONFIG["token"])
        .build()
    )

    # فرمان‌ها
    app.add_handler(CommandHandler("start", on_start))
    app.add_handler(CommandHandler("summon", on_summon))
    app.add_handler(CommandHandler("oath", on_oath))
    app.add_handler(CallbackQueryHandler(on_oath_accept, pattern=r"^oath_accept$"))

    app.add_handler(CommandHandler("mode", on_mode))
    app.add_handler(CallbackQueryHandler(on_mode_button, pattern=r"^mode_"))

    app.add_handler(CommandHandler("edict", on_edict))
    app.add_handler(CommandHandler("veil", on_veil))
    app.add_handler(CommandHandler("status", on_status))

    # پیام‌های عمومی برای لحن مالک
    app.add_handler(MessageHandler(filters.ALL, on_message_tone))

    # Polling
    await app.initialize()
    await app.start()
    print("[legend-bot] polling started (python)")
    try:
        await asyncio.Event().wait()
    finally:
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
