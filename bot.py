import telebot
from telebot import types
import sqlite3
import threading
import time
import re
from datetime import datetime

# —————————————————————————————————————————————
TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
OWNER_ID = 7341748124
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
time.sleep(1)

# اتصال به دیتابیس
conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

# ایجاد جدول کاربران
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id      INTEGER PRIMARY KEY,
    name         TEXT,
    username     TEXT,
    coin         INTEGER DEFAULT 180,
    score        INTEGER DEFAULT 250,
    gold_tick    INTEGER DEFAULT 0,
    role         TEXT DEFAULT 'ممبر عادی 🧍',
    birthdate    TEXT,
    partner_id   INTEGER,
    child_of     INTEGER,
    pet          TEXT,
    custom_emoji TEXT,
    sect         TEXT,
    is_admin     INTEGER DEFAULT 0,
    is_blocked   INTEGER DEFAULT 0
)
''')
# ایجاد جدول فرقه‌ها
c.execute('''
CREATE TABLE IF NOT EXISTS sects (
    name     TEXT PRIMARY KEY,
    owner_id INTEGER
)
''')
conn.commit()

# دیکشنری مقام‌ها
ranks = {
    "m1": "سوگولی گروه 💋", "m2": "پرنسس گروه 👑", "m3": "ملکه گروه 👸",
    "m4": "شوالیه گروه 🛡️", "m5": "رهبر گروه 🦁", "m6": "اونر گروه 🌀",
    "m7": "زامبی الفا گروه 🧟‍♂️", "m8": "نفس گروه 💨", "m9": "بادیگارد گروه 🕶️",
    "m10": "ممبر عادی 🧍", "m11": "عاشق دلباخته ❤️‍🔥", "m12": "برده گروه 🧎",
    "m13": "رئیس گروه 🧠", "m14": "کصشرگوی گروه 🐵", "m15": "دختر شاه 👑👧"
}

# حافظه موقت برای درخواست‌ها
pending_loves = {}
pending_children = {}
pending_sect_invites = {}
sect_ranking_cache = []
sect_ranking_timestamp = 0

# —————————————————————————————————————————————
# توابع کمکی
def add_user(uid, name, uname):
    c.execute("SELECT 1 FROM users WHERE user_id=?", (uid,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users(user_id,name,username) VALUES(?,?,?)",
            (uid, name, uname)
        )
        conn.commit()

def get_username(uid):
    if not uid:
        return "ندارد ❌"
    c.execute("SELECT username FROM users WHERE user_id=?", (uid,))
    r = c.fetchone()
    return r[0] if r and r[0] else "ندارد ❌"

def get_rank(score):
    if score < 500:   return "تازه‌کار 👶"
    if score < 1000:  return "حرفه‌ای 🔥"
    if score < 2000:  return "استاد 🌟"
    if score < 4000:  return "قهرمان 🏆"
    if score < 7000:  return "افسانه‌ای 🐉"
    if score < 10000: return "بی‌نظیر 💎"
    return "اسطوره 🚀"

def is_admin(uid):
    if uid == OWNER_ID:
        return True
    c.execute("SELECT is_admin FROM users WHERE user_id=?", (uid,))
    r = c.fetchone()
    return bool(r and r[0] == 1)

def check_blocked(uid):
    c.execute("SELECT is_blocked FROM users WHERE user_id=?", (uid,))
    r = c.fetchone()
    return bool(r and r[0] == 1)

def blocked_guard(f):
    def wrapper(m):
        add_user(m.from_user.id, m.from_user.first_name, m.from_user.username or "ندارد")
        if check_blocked(m.from_user.id):
            bot.reply_to(m, "❌ حساب شما در حالت تعلیق است!")
            return
        return f(m)
    return wrapper

# به‌روزرسانی رتبه‌بندی فرقه‌ها هر ساعت
def update_sect_ranking():
    global sect_ranking_cache, sect_ranking_timestamp
    while True:
        rows = c.execute(
            "SELECT sect, COUNT(*) cnt FROM users "
            "WHERE sect IS NOT NULL GROUP BY sect "
            "ORDER BY cnt DESC LIMIT 10"
        ).fetchall()
        sect_ranking_cache = rows
        sect_ranking_timestamp = time.time()
        time.sleep(3600)

threading.Thread(target=update_sect_ranking, daemon=True).start()

# —————————————————————————————————————————————
# START / HELP / BOT RANKS
@bot.message_handler(commands=['start'])
@blocked_guard
def cmd_start(m):
    txt = f'''
سلام @{m.from_user.username}! 🌹
برای پروفایل      /my
عشق‌بازی         /love (ریپلای)
طلاق             /dlove
انتقال سکه       /give
ثبت پت           /pet <نام>
حذف پت           /unpet
درخواست فرزند     /child
حذف فرزند        /dchild
ایموجی           /emoji <ایموجی>
حذف ایموجی       /reemoji
فرقه‌سازی        /sectcreate <نام>
دعوت فرقه        /sectinvite
خروج فرقه        /sectleave
انحلال فرقه      /sectdisband
اخراج فرقه       /dferghe
لیست فرقه‌ها     /rank
اطلاعات فرقه     /mee
بلاک کاربر       /block (ریپلای)
رفع بلاک         /dblock (ریپلای)
فروشگاه         /shop
طلسم پاک‌سازی   /del
طلسم سکوت       /mut
'''
    bot.reply_to(m, txt)

@bot.message_handler(commands=['help'])
@blocked_guard
def cmd_help(m):
    bot.reply_to(m,
        "/start /my /love /dlove /give /pet /unpet /child /dchild /emoji /reemoji\n"
        "/sectcreate /sectinvite /sectleave /sectdisband /dferghe /rank /mee\n"
        "/block /dblock /shop /del /mut +500 -500 +100 🪙 -100 🪙 /tik /dtik"
    )

@bot.message_handler(commands=['ranks'])
@blocked_guard
def cmd_bot_ranks(m):
    txt = "📜 مقام‌های ربات:\n" + "\n".join(f"{k} — {v}" for k, v in ranks.items())
    bot.reply_to(m, txt)

# —————————————————————————————————————————————
# PROFILE / OLD (نسخه اورجینال پروفایل)
@bot.message_handler(commands=['my'])
@blocked_guard
def cmd_my(m):
    if m.reply_to_message and is_admin(m.from_user.id):
        target = m.reply_to_message.from_user.id
    else:
        target = m.from_user.id

    add_user(target,
             m.reply_to_message.from_user.first_name if m.reply_to_message else m.from_user.first_name,
             get_username(target))

    c.execute("SELECT * FROM users WHERE user_id=?", (target,))
    d = c.fetchone()
    if not d:
        return bot.reply_to(m, "❌ خطا در بازیابی پروفایل.")

    c.execute("SELECT username FROM users WHERE child_of=?", (target,))
    childs = [f"@{r[0]}" for r in c.fetchall()]
    children_txt = ", ".join(childs) if childs else ""

    text = f'''
━━━【 پروفایل شما در گروه 】━━━

•مشخصات فردی شما•
👤 نام: {d[1]}
✨ یوزرنیم: @{d[2]}
⚔️ آیدی عددی: {d[0]}

🌐 کشور شما: 🇮🇷 ایران

•• دارایی‌ها و امتیازت: ••
💰 سکه‌هات: {d[3]}
💎 امتیازت: {d[4]}
⚜️ نشان تایید طلایی: {"دارد ✅" if d[5]==1 else "ندارد ❌"}

•مشخصات خانواده شما•
😍 اسم همسر یا عشق‌ِت: {get_username(d[8])}
♥️ اسم فرزندتون: {children_txt}
🐣 حیوان خانگی شما: {d[10] or ""}
♨️ فرقه‌ای که توش عضوی: {d[12] or ""}

🌙 شکلک اختصاصی: {d[11] or ""}
🎂 تاریخ تولدت: {d[7] or "ثبت نشده ❌"}
🔮 قدرت‌ها و طلسم‌ها: (نحوه اجرا /shop)

:: در گروه :::::

▪︎🏆 درجه شما در گروه: {get_rank(d[4])}
▪︎💠 مقام شما در گروه: {d[6]}
'''
    bot.reply_to(m, text)

@bot.message_handler(commands=['old'])
@blocked_guard
def cmd_old(m):
    m0 = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', m.text.strip())
    if not m0:
        return bot.reply_to(m, "❌ فرمت صحیح: /old 1379/1/11")
    bd, uid = m0.group(1), m.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if (row := c.fetchone()) is None or row[0] < 40:
        return bot.reply_to(m, "❌ سکه کافی نیست!")
    c.execute("UPDATE users SET birthdate=?,coin=coin-40 WHERE user_id=?", (bd, uid))
    conn.commit()
    bot.reply_to(m, "🎂 ثبت تولد انجام شد و ۴۰ سکه کسر گردید.")

# —————————————————————————————————————————————
# LOVE & DIVORCE
@bot.message_handler(commands=['love'])
@blocked_guard
def cmd_love(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "❌ ریپلای کنید روی پیام طرف مقابل.")
    rid, sid = m.from_user.id, m.reply_to_message.from_user.id
    if rid == sid:
        return bot.reply_to(m, "❌ نمی‌توانید با خودتان ازدواج کنید!")
    add_user(rid, m.from_user.first_name, m.from_user.username or "ندارد")
    add_user(sid, m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.username or "ندارد")
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("💖 قبول می‌کنم", callback_data=f"accept_{rid}"),
        types.InlineKeyboardButton("💔 قبول نمی‌کنم", callback_data=f"reject_{rid}")
    )
    txt = f"💌 @{m.from_user.username} درخواست ازدواج به @{m.reply_to_message.from_user.username} داد!\nقبول می‌کنی؟"
    sent = bot.send_message(m.chat.id, txt, reply_markup=kb)
    pending_loves[sent.message_id] = rid

@bot.callback_query_handler(lambda call: call.data.startswith("accept_") or call.data.startswith("reject_"))
def cb_love(call):
    mid = call.message.message_id
    if mid not in pending_loves:
        return bot.answer_callback_query(call.id, "❌ درخواست منقضی شد.")
    rid = pending_loves[mid]; sid = call.from_user.id
    if call.data.startswith("accept_"):
        c.execute("SELECT coin FROM users WHERE user_id=?", (rid,))
        if c.fetchone()[0] < 40:
            bot.edit_message_text("❌ سکه کافی نیست!", call.message.chat.id, mid)
            del pending_loves[mid]
            return
        c.execute("UPDATE users SET partner_id=?,coin=coin-40 WHERE user_id=?", (sid, rid))
        c.execute("UPDATE users SET partner_id=? WHERE user_id=?", (rid, sid))
        conn.commit()
        bot.edit_message_text("💒 ازدواج ثبت شد! مبارک باشید! 🎉", call.message.chat.id, mid)
        bot.send_message(call.message.chat.id, f"🎊 @{get_username(rid)} و @{get_username(sid)} زوج شدند! 💘")
    else:
        bot.edit_message_text("💔 درخواست رد شد.", call.message.chat.id, mid)
    del pending_loves[mid]

@bot.message_handler(commands=['dlove'])
@blocked_guard
def cmd_dlove(m):
    uid = m.from_user.id
    c.execute("SELECT partner_id FROM users WHERE user_id=?", (uid,))
    row = c.fetchone()
    if not row or not row[0]:
        return bot.reply_to(m, "❌ شما ازدواج نکرده‌اید.")
    pid = row[0]
    c.execute("UPDATE users SET partner_id=NULL WHERE user_id IN(?,?)", (uid, pid))
    conn.commit()
    bot.send_message(m.chat.id, f"💔 @{get_username(uid)} و @{get_username(pid)} از هم جدا شدند. 😢")

# —————————————————————————————————————————————
# PET SYSTEM
@bot.message_handler(commands=['pet'])
@blocked_guard
def cmd_pet(m):
    parts = m.text.strip().split(maxsplit=1)
    if len(parts) != 2:
        return bot.reply_to(m, "❌ فرمت صحیح: /pet نام‌حیوان")
    pet = parts[1]; uid = m.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if c.fetchone()[0] < 40:
        return bot.reply_to(m, "❌ سکه کافی نیست!")
    c.execute("UPDATE users SET pet=?,coin=coin-40 WHERE user_id=?", (pet, uid))
    conn.commit()
    bot.reply_to(m, f"🐾 پت `{pet}` ثبت شد و ۴۰ سکه کسر گردید.", parse_mode="Markdown")

@bot.message_handler(commands=['unpet'])
@blocked_guard
def cmd_unpet(m):
    uid = m.from_user.id
    c.execute("SELECT pet FROM users WHERE user_id=?", (uid,))
    if not c.fetchone()[0]:
        return bot.reply_to(m, "❌ شما هیچ پت ندارید!")
    c.execute("UPDATE users SET pet=NULL WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m, "🐾 پت شما حذف شد.")

# —————————————————————————————————————————————
# CHILD SYSTEM
@bot.message_handler(commands=['child'])
@blocked_guard
def cmd_child(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "❌ برای درخواست فرزند ریپلای کنید.")
    rid, sid = m.from_user.id, m.reply_to_message.from_user.id
    if rid == sid:
        return bot.reply_to(m, "❌ نمی‌توانید فرزند خودتان باشید!")
    add_user(rid, m.from_user.first_name, m.from_user.username or "ندارد")
    add_user(sid, m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.username or "ندارد")
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("👶 قبول می‌کنم", callback_data=f"caccept_{rid}"),
        types.InlineKeyboardButton("❌ قبول نمی‌کنم", callback_data=f"creject_{rid}")
    )
    txt = f"👪 @{m.from_user.username} درخواست فرزند شدن به @{m.reply_to_message.from_user.username} داد!\nقبول می‌کنی؟"
    sent = bot.send_message(m.chat.id, txt, reply_markup=kb)
    pending_children[sent.message_id] = rid

@bot.callback_query_handler(lambda call: call.data.startswith("caccept_") or call.data.startswith("creject_"))
def cb_child(call):
    mid = call.message.message_id
    if mid not in pending_children:
        return bot.answer_callback_query(call.id, "❌ درخواست منقضی شد.")
    rid = pending_children[mid]; sid = call.from_user.id
    if call.data.startswith("caccept_"):
        c.execute("SELECT coin FROM users WHERE user_id=?", (rid,))
        if c.fetchone()[0] < 40:
            bot.edit_message_text("❌ سکه کافی نیست!", call.message.chat.id, mid)
            del pending_children[mid]
            return
        c.execute("UPDATE users SET child_of=?,coin=coin-40 WHERE user_id=?", (sid, rid))
        conn.commit()
        bot.edit_message_text("👶 فرزند پذیرفته شد!", call.message.chat.id, mid)
        bot.send_message(call.message.chat.id, f"🎉 @{get_username(rid)} فرزند @{get_username(sid)} شد!")
    else:
        bot.edit_message_text("❌ درخواست رد شد.", call.message.chat.id, mid)
    del pending_children[mid]

@bot.message_handler(commands=['dchild'])
@blocked_guard
def cmd_dchild(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "❌ برای حذف فرزند ریپلای کنید.")
    victim = m.reply_to_message.from_user.id; uid = m.from_user.id
    c.execute("SELECT child_of FROM users WHERE user_id=?", (victim,))
    row = c.fetchone()
    if not row or row[0] != uid:
        return bot.reply_to(m, "❌ رابطه‌ای وجود ندارد.")
    c.execute("UPDATE users SET child_of=NULL WHERE user_id=?", (victim,))
    conn.commit()
    bot.reply_to(m, f"🚼 @{get_username(victim)} از خانواده حذف شد.")

# —————————————————————————————————————————————
# EMOJI SYSTEM
@bot.message_handler(commands=['emoji'])
@blocked_guard
def cmd_emoji(m):
    parts = m.text.strip().split(maxsplit=1)
    if len(parts) != 2:
        return bot.reply_to(m, "❌ فرمت صحیح: /emoji 😎")
    em, uid = parts[1], m.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if c.fetchone()[0] < 50:
        return bot.reply_to(m, "❌ سکه کافی نیست!")
    c.execute("UPDATE users SET custom_emoji=?,coin=coin-50 WHERE user_id=?", (em, uid))
    conn.commit()
    bot.reply_to(m, f"🎭 ایموجی `{em}` ثبت شد و ۵۰ سکه کسر گردید.", parse_mode="Markdown")

@bot.message_handler(commands=['reemoji'])
@blocked_guard
def cmd_reemoji(m):
    uid = m.from_user.id
    c.execute("SELECT custom_emoji FROM users WHERE user_id=?", (uid,))
    if not c.fetchone()[0]:
        return bot.reply_to(m, "❌ خبری از ایموجی نیست!")
    c.execute("UPDATE users SET custom_emoji=NULL WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m, "🎭 ایموجی شما حذف شد.")

# —————————————————————————————————————————————
# COIN & SCORE CONTROLS (OWNER/ADMINS)
@bot.message_handler(func=lambda m: m.reply_to_message and bool(re.match(r'^(\+|\-)', m.text.strip())))
def control_points(m):
    uid = m.from_user.id
    if not (uid == OWNER_ID or is_admin(uid)):
        return
    target = m.reply_to_message.from_user.id
    text = m.text.strip()
    # امتیاز: +500 یا -500
    m_add = re.match(r'^\+ (\d+)$', text)
    m_sub = re.match(r'^\- (\d+)$', text)
    # سکه: +100 🪙 یا -100 🪙
    c_add = re.match(r'^\+ (\d+)\s+🪙$', text)
    c_sub = re.match(r'^\- (\d+)\s+🪙$', text)

    if m_add:
        amt = int(m_add.group(1))
        c.execute("UPDATE users SET score=score+? WHERE user_id=?", (amt, target))
        conn.commit()
        bot.reply_to(m, f"🎉 {amt} امتیاز به @{get_username(target)} اضافه شد!")
    elif m_sub:
        amt = int(m_sub.group(1))
        c.execute("UPDATE users SET score=score-? WHERE user_id=?", (amt, target))
        conn.commit()
        bot.reply_to(m, f"💔 {amt} امتیاز از @{get_username(target)} کسر شد!")
    elif c_add:
        amt = int(c_add.group(1))
        c.execute("UPDATE users SET coin=coin+? WHERE user_id=?", (amt, target))
        conn.commit()
        bot.reply_to(m, f"💰 {amt} سکه به @{get_username(target)} اضافه شد!")
    elif c_sub:
        amt = int(c_sub.group(1))
        c.execute("UPDATE users SET coin=coin-? WHERE user_id=?", (amt, target))
        conn.commit()
        bot.reply_to(m, f"💸 {amt} سکه از @{get_username(target)} کسر شد!")

# —————————————————————————————————————————————
# GOLD TICK
@bot.message_handler(commands=['tik'])
def cmd_tik(m):
    if not m.reply_to_message:
        return
    uid = m.from_user.id
    target = m.reply_to_message.from_user.id
    if not (uid == OWNER_ID or is_admin(uid)):
        return
    c.execute("UPDATE users SET gold_tick=1 WHERE user_id=?", (target,))
    conn.commit()
    bot.reply_to(m, f"⚜️ نشان تایید طلایی به @{get_username(target)} داده شد!")

@bot.message_handler(commands=['dtik'])
def cmd_dtik(m):
    if not m.reply_to_message:
        return
    uid = m.from_user.id
    target = m.reply_to_message.from_user.id
    if not (uid == OWNER_ID or is_admin(uid)):
        return
    c.execute("UPDATE users SET gold_tick=0 WHERE user_id=?", (target,))
    conn.commit()
    bot.reply_to(m, f"❌ نشان تایید طلایی از @{get_username(target)} برداشته شد.")

# —————————————————————————————————————————————
# ADMIN MANAGEMENT
@bot.message_handler(commands=['admin'])
def cmd_admin(m):
    if m.from_user.id != OWNER_ID or not m.reply_to_message:
        return
    uid = m.reply_to_message.from_user.id
    add_user(uid, m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.username or "ندارد")
    c.execute("UPDATE users SET is_admin=1 WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m, f"✅ @{get_username(uid)} مدیر ربات شد.")

@bot.message_handler(commands=['dadmin'])
def cmd_dadmin(m):
    if m.from_user.id != OWNER_ID or not m.reply_to_message:
        return
    uid = m.reply_to_message.from_user.id
    c.execute("UPDATE users SET is_admin=0 WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m, f"❌ @{get_username(uid)} از مدیران حذف شد.")

@bot.message_handler(commands=['ddadmin'])
def cmd_ddadmin(m):
    if m.from_user.id != OWNER_ID:
        return
    c.execute("UPDATE users SET is_admin=0")
    conn.commit()
    bot.reply_to(m, "👢 همه مدیران حذف شدند.")

# —————————————————————————————————————————————
# SECT SYSTEM
@bot.message_handler(commands=['sectcreate'])
@blocked_guard
def cmd_sectcreate(m):
    pts = m.text.strip().split(maxsplit=1)
    if len(pts) != 2:
        return bot.reply_to(m, "❌ فرمت صحیح: /sectcreate نام_فرقه")
    name, uid = pts[1], m.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if c.fetchone()[0] < 200:
        return bot.reply_to(m, "❌ سکه کافی نیست!")
    try:
        c.execute("INSERT INTO sects(name,owner_id) VALUES(?,?)", (name, uid))
        c.execute("UPDATE users SET sect=?,coin=coin-200 WHERE user_id=?", (name, uid))
        conn.commit()
        bot.reply_to(m, f"🌀 فرقه `{name}` ساخته شد و ۲۰۰ سکه کسر شد.", parse_mode="Markdown")
    except:
        bot.reply_to(m, "❌ این فرقه قبلاً وجود دارد!")

@bot.message_handler(commands=['sectinvite'])
@blocked_guard
def cmd_sectinvite(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "❌ ریپلای کنید برای دعوت.")
    inviter = m.from_user.id
    c.execute("SELECT sect FROM users WHERE user_id=?", (inviter,))
    row = c.fetchone()
    if not row or not row[0]:
        return bot.reply_to(m, "❌ شما عضو هیچ فرقه‌ای نیستید!")
    sect = row[0]
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ می‌پذیرم", callback_data=f"saccept_{inviter}"),
        types.InlineKeyboardButton("❌ نمی‌خواهم", callback_data=f"sreject_{inviter}")
    )
    uname = m.reply_to_message.from_user.username
    sent = bot.send_message(
        m.chat.id,
        f"🌀 @{uname} به فرقه‌ی `{sect}` دعوت شد. می‌پذیری؟",
        reply_markup=kb, parse_mode="Markdown"
    )
    pending_sect_invites[sent.message_id] = inviter

@bot.callback_query_handler(lambda call: call.data.startswith("saccept_") or call.data.startswith("sreject_"))
def cb_sectinvite(call):
    mid = call.message.message_id
    if mid not in pending_sect_invites:
        return bot.answer_callback_query(call.id, "❌ درخواست منقضی شد.")
    inv = pending_sect_invites[mid]
    res = call.from_user.id
    if call.data.startswith("saccept_"):
        c.execute("SELECT sect FROM users WHERE user_id=?", (inv,))
        sect = c.fetchone()[0]
        c.execute("UPDATE users SET sect=? WHERE user_id=?", (sect, res))
        conn.commit()
        bot.edit_message_text(f"✅ خوش آمدی به فرقه‌ی `{sect}`!", call.message.chat.id, mid, parse_mode="Markdown")
    else:
        bot.edit_message_text("❌ دعوت رد شد.", call.message.chat.id, mid)
    del pending_sect_invites[mid]

@bot.message_handler(commands=['sectleave'])
@blocked_guard
def cmd_sectleave(m):
    uid = m.from_user.id
    c.execute("SELECT sect FROM users WHERE user_id=?", (uid,))
    if not c.fetchone()[0]:
        return bot.reply_to(m, "❌ شما عضو هیچ فرقه‌ای نیستید!")
    c.execute("UPDATE users SET sect=NULL WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m, "🌀 شما از فرقه خارج شدید.")

@bot.message_handler(commands=['sectdisband'])
@blocked_guard
def cmd_sectdisband(m):
    uid = m.from_user.id
    c.execute("SELECT name FROM sects WHERE owner_id=?", (uid,))
    row = c.fetchone()
    if not row:
        return bot.reply_to(m, "❌ شما مالک هیچ فرقه‌ای نیستید!")
    name = row[0]
    c.execute("DELETE FROM sects WHERE name=?", (name,))
    c.execute("UPDATE users SET sect=NULL WHERE sect=?", (name,))
    conn.commit()
    bot.reply_to(m, f"🌀 فرقه `{name}` منحل شد!", parse_mode="Markdown")

@bot.message_handler(commands=['dferghe'])
@blocked_guard
def cmd_dferghe(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "❌ برای اخراج ریپلای کنید.")
    kicker = m.from_user.id
    victim = m.reply_to_message.from_user.id
    c.execute("SELECT name FROM sects WHERE owner_id=?", (kicker,))
    row = c.fetchone()
    if not row:
        return bot.reply_to(m, "❌ شما مالک فرقه نیستید!")
    name = row[0]
    c.execute("SELECT sect FROM users WHERE user_id=?", (victim,))
    if c.fetchone()[0] != name:
        return bot.reply_to(m, "❌ فرد مورد نظر عضو فرقه‌ی شما نیست!")
    c.execute("UPDATE users SET sect=NULL WHERE user_id=?", (victim,))
    conn.commit()
    bot.reply_to(m, f"👢 @{get_username(victim)} از فرقه‌ی `{name}` اخراج شد.", parse_mode="Markdown")

# —————————————————————————————————————————————
# TOP SECTS / MEE / BLOCK
@bot.message_handler(commands=['rank'])
@blocked_guard
def cmd_rank(m):
    if not sect_ranking_cache:
        return bot.reply_to(m, "⏳ رتبه‌بندی در حال محاسبه است...")
    txt = f"📊 لیست ۱۰ فرقه برتر تا {datetime.now().strftime('%H:%M')}:\n"
    for sect, cnt in sect_ranking_cache:
        txt += f"• `{sect}` ({cnt} عضو)\n"
    bot.reply_to(m, txt, parse_mode="Markdown")

@bot.message_handler(commands=['mee'])
@blocked_guard
def cmd_mee(m):
    uid = m.from_user.id
    c.execute("SELECT sect FROM users WHERE user_id=?", (uid,))
    row = c.fetchone()
    if not row or not row[0]:
        return bot.reply_to(m, "❌ شما عضو هیچ فرقه‌ای نیستید!")
    sect = row[0]
    total = c.execute("SELECT COUNT(*) FROM users WHERE sect=?", (sect,)).fetchone()[0]
    rank_pos = next((i+1 for i,(s,_) in enumerate(sect_ranking_cache) if s==sect), "–")
    bot.reply_to(m,
        f"🌀 اطلاعات فرقه‌ی `{sect}`:\n"
        f"• تعداد اعضا: {total}\n"
        f"• رتبه در گروه: {rank_pos}\n", parse_mode="Markdown"
    )

@bot.message_handler(commands=['block'])
def cmd_block(m):
    if not (m.from_user.id == OWNER_ID or is_admin(m.from_user.id)) or not m.reply_to_message:
        return
    uid = m.reply_to_message.from_user.id
    c.execute("UPDATE users SET is_blocked=1 WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m, f"🔒 @{get_username(uid)} مسدود شد.")

@bot.message_handler(commands=['dblock'])
def cmd_dblock(m):
    if not (m.from_user.id == OWNER_ID or is_admin(m.from_user.id)) or not m.reply_to_message:
        return
    uid = m.reply_to_message.from_user.id
    c.execute("UPDATE users SET is_blocked=0 WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m, f"🔓 @{get_username(uid)} رفع مسدودیت شد.")

# —————————————————————————————————————————————
# SHOP / SPELLS
@bot.message_handler(commands=['shop'])
@blocked_guard
def cmd_shop(m):
    bot.reply_to(m, '''
🎁 فروشگاه طلسم‌ها:
1️⃣ 🧼 پاک‌سازی پیام (/del) – ۲۰ سکه  
2️⃣ 🧊 حبس یخی (/mut)      – ۸۰ سکه
''')

@bot.message_handler(commands=['del'])
@blocked_guard
def cmd_del(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "❌ برای پاک‌سازی ریپلای کنید.")
    uid = m.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if c.fetchone()[0] < 20:
        return bot.reply_to(m, "❌ سکه کافی نیست!")
    try:
        bot.delete_message(m.chat.id, m.reply_to_message.message_id)
        c.execute("UPDATE users SET coin=coin-20 WHERE user_id=?", (uid,))
        conn.commit()
        bot.reply_to(m, "✅ پیام پاک شد و ۲۰ سکه کسر گردید.")
    except Exception as e:
        bot.reply_to(m, f"❌ خطا: {e}")

@bot.message_handler(commands=['mut'])
@blocked_guard
def cmd_mut(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "❌ برای حبس یخی ریپلای کنید.")
    uid = m.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if c.fetchone()[0] < 80:
        return bot.reply_to(m, "❌ سکه کافی نیست!")
    try:
        bot.restrict_chat_member(
            chat_id=m.chat.id,
            user_id=m.reply_to_message.from_user.id,
            until_date=int(time.time()) + 60,
            can_send_messages=False
        )
        c.execute("UPDATE users SET coin=coin-80 WHERE user_id=?", (uid,))
        conn.commit()
        bot.reply_to(m, "🧊 کاربر ۶۰ ثانیه سکوت شد و ۸۰ سکه کسر گردید.")
    except Exception as e:
        bot.reply_to(m, f"❌ خطا: {e}")

# —————————————————————————————————————————————
bot.infinity_polling()
