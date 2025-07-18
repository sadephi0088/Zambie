import telebot
from telebot import types
import sqlite3
import re
import time

TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
OWNER_ID = 7341748124
bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()
time.sleep(1)

# اتصال به دیتابیس
conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

# ایجاد جدول users با همه ستون‌های لازم
try:
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id     INTEGER PRIMARY KEY,
        name        TEXT,
        username    TEXT,
        coin        INTEGER DEFAULT 180,
        score       INTEGER DEFAULT 250,
        gold_tick   INTEGER DEFAULT 0,
        role        TEXT DEFAULT 'ممبر عادی 🧍',
        birthdate   TEXT,
        partner_id  INTEGER,
        is_admin    INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
except:
    pass

# اگر ستون partner_id یا is_admin حذف شده بود، دوباره اضافه‌اش می‌کنیم
for col, col_type in (("partner_id","INTEGER"), ("is_admin","INTEGER")):
    try:
        c.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type} DEFAULT 0")
        conn.commit()
    except:
        pass

# دیکشنری مقام‌ها
ranks = {
    "m1": "سوگولی گروه 💋",
    "m2": "پرنسس گروه 👑",
    "m3": "ملکه گروه 👸",
    "m4": "شوالیه گروه 🛡️",
    "m5": "رهبر گروه 🦁",
    "m6": "اونر گروه 🌀",
    "m7": "زامبی الفا گروه 🧟‍♂️",
    "m8": "نفس گروه 💨",
    "m9": "بادیگارد گروه 🕶️",
    "m10": "ممبر عادی 🧍",
    "m11": "عاشق دلباخته ❤️‍🔥",
    "m12": "برده گروه 🧎",
    "m13": "رئیس گروه 🧠",
    "m14": "کصشرگوی گروه 🐵",
    "m15": "دختر شاه 👑👧"
}

# حافظه موقت درخواست‌های عشق
pending_loves = {}

def add_user(message):
    """اگر کاربر جدید است، در جدول ثبتش کن."""
    uid = message.from_user.id
    name = message.from_user.first_name
    uname = message.from_user.username or "ندارد"
    c.execute("SELECT 1 FROM users WHERE user_id = ?", (uid,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)",
                  (uid, name, uname))
        conn.commit()

def get_username(user_id):
    """یوزرنیم از دیتابیس می‌گیرد."""
    if not user_id:
        return "ندارد ❌"
    c.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    return row[0] if row else "ندارد ❌"

def get_rank(score):
    """تبدیل امتیاز به درجه."""
    if score < 500:
        return "تازه‌کار 👶"
    if score < 1000:
        return "حرفه‌ای 🔥"
    if score < 2000:
        return "استاد 🌟"
    if score < 4000:
        return "قهرمان 🏆"
    if score < 7000:
        return "افسانه‌ای 🐉"
    if score < 10000:
        return "بی‌نظیر 💎"
    return "اسطوره 🚀"

# —————————————————————————————————————————————
# START / HELP / RANKS
@bot.message_handler(commands=['start'])
def start_handler(message):
    add_user(message)
    text = f'''
سلام @{message.from_user.username} عزیز! 🌹
به ربات ما خوش اومدی.
برای پروفایل /my
برای عشق‌بازی /love (ریپلای)
برای طلاق /dlove
برای فروشگاه /shop
برای ثبت تولد /old
برای لیست مقام‌ها /ranks
برای راهنما /help
'''
    bot.reply_to(message, text)

@bot.message_handler(commands=['help'])
def help_handler(message):
    text = '''
📖 راهنما:

/start    – خوش‌آمدگویی  
/my       – نمایش پروفایل  
/love     – درخواست عشق (ریپلای روی پیام)  
/dlove    – پایان رابطه  
/give     – انتقال سکه (ریپلای + مقدار)  
/shop     – فروشگاه طلسم‌ها  
/old      – ثبت تاریخ تولد (۴۰ سکه)  
/ranks    – لیست مقام‌ها  
/admin    – افزودن مدیر (مالک ریپلای)  
/dadmin   – حذف مدیر (مالک ریپلای)  
/ddadmin  – حذف همه مدیران (مالک)  
/tik      – طلسم طلایی (مالک ریپلای)  
/dtik     – برداشتن طلسم طلایی (مالک ریپلای)  
/del      – طلسم بپاک (ریپلای +۲۰ سکه)  
/mut      – طلسم حبس یخی (ریپلای +۸۰ سکه)  
'''
    bot.reply_to(message, text)

@bot.message_handler(commands=['ranks'])
def ranks_handler(message):
    text = "📜 مقام‌های گروه:\n"
    for key, val in ranks.items():
        text += f"{key} — {val}\n"
    bot.reply_to(message, text)

# —————————————————————————————————————————————
# PROFILE / OLD
@bot.message_handler(commands=['my'])
def show_profile(message):
    add_user(message)
    uid = message.from_user.id
    c.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    data = c.fetchone()
    if not data:
        bot.reply_to(message, "❌ خطا در بازیابی پروفایل.")
        return

    tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"
    rank = get_rank(data[4])
    role = data[6] or "ممبر عادی 🧍"
    birthdate = data[7] or "ثبت نشده ❌"
    partner_username = get_username(data[8])

    text = f'''
━━━【 پروفایل شما در گروه 】━━━

•مشخصات فردی شما•
👤 نام: {data[1]}
✨ یوزرنیم: @{data[2]}
⚔️ آیدی عددی: {data[0]}

🌐 کشور شما: 🇮🇷 ایران

•• دارایی‌ها و امتیازت: ••
💰 سکه‌هات: {data[3]}
💎 امتیازت: {data[4]}
⚜️ نشان تایید طلایی: {tick}

•مشخصات خانواده شما•
😍 اسم همسر یا عشق‌ِت: {partner_username}
♥️ اسم فرزندتون:
🐣 حیوان خانگی شما:
♨️ فرقه‌ای که توش عضوی:

🌙 شکلک اختصاصی:
🎂 تاریخ تولدت: {birthdate}
🔮 قدرت‌ها و طلسم‌ها: (نحوه اجرا /shop)

:: در گروه :::::

▪︎🏆 درجه شما در گروه: {rank}
▪︎💠 مقام شما در گروه: {role}
'''
    bot.reply_to(message, text)

@bot.message_handler(commands=['old'])
def set_birthdate(message):
    uid = message.from_user.id
    m = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', message.text.strip())
    if not m:
        bot.reply_to(message, "❌ فرمت نادرسته. مثال:\n/old 1379/1/11")
        return
    bd = m.group(1)
    c.execute("SELECT coin FROM users WHERE user_id = ?", (uid,))
    row = c.fetchone()
    if not row or row[0] < 40:
        bot.reply_to(message, "❌ سکه کافی نداری!")
        return
    c.execute("UPDATE users SET birthdate = ?, coin = coin - 40 WHERE user_id = ?",
              (bd, uid))
    conn.commit()
    bot.reply_to(message, "🎂 تولد ثبت شد و ۴۰ سکه کسر گردید.")

# —————————————————————————————————————————————
# LOVE & DIVORCE
@bot.message_handler(commands=['love'])
def love_request(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ ریپلای کنید روی پیام طرف مقابل.")
        return

    requester = message.from_user
    target = message.reply_to_message.from_user
    if requester.id == target.id:
        bot.reply_to(message, "❌ نمی‌تونی با خودت ازدواج کنی!")
        return

    add_user(message)
    add_user(message.reply_to_message)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💖 قبول می‌کنم", callback_data=f"accept_{requester.id}"),
        types.InlineKeyboardButton("💔 قبول نمی‌کنم", callback_data=f"reject_{requester.id}")
    )

    txt = (f"🎯 @{target.username}\n"
           f"💌 @{requester.username} عاشقته و می‌خواد باهات ازدواج کنه!\n\n"
           "آیا عشقش رو قبول می‌کنی؟ 😍")
    sent = bot.send_message(message.chat.id, txt, reply_markup=markup)
    pending_loves[sent.message_id] = requester.id

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("accept_") or call.data.startswith("reject_")
)
def handle_love_response(call):
    mid = call.message.message_id
    if mid not in pending_loves:
        bot.answer_callback_query(call.id, "❌ منقضی شده.")
        return

    req_id = pending_loves[mid]
    res_id = call.from_user.id

    if call.data.startswith("accept_"):
        c.execute("SELECT coin FROM users WHERE user_id = ?", (req_id,))
        if c.fetchone()[0] < 40:
            bot.edit_message_text("❌ سکه درخواست‌کننده کافیش نیست!",
                                  call.message.chat.id, mid)
            del pending_loves[mid]
            return

        c.execute("UPDATE users SET partner_id = ? WHERE user_id = ?", (res_id, req_id))
        c.execute("UPDATE users SET partner_id = ? WHERE user_id = ?", (req_id, res_id))
        c.execute("UPDATE users SET coin = coin - 40 WHERE user_id = ?", (req_id,))
        conn.commit()

        bot.edit_message_text("💖 عشق پذیرفته شد! تبریک به این زوج! 🎉",
                              call.message.chat.id, mid)
        bot.send_message(call.message.chat.id,
                         f"🎊 @{get_username(req_id)} و @{get_username(res_id)} حالا عاشق هم هستن! 💘")
    else:
        bot.edit_message_text("💔 عشق رد شد. شاید یه روز دیگه... 😢",
                              call.message.chat.id, mid)

    del pending_loves[mid]

@bot.message_handler(commands=['dlove'])
def divorce_love(message):
    uid = message.from_user.id
    c.execute("SELECT partner_id FROM users WHERE user_id = ?", (uid,))
    row = c.fetchone()
    if not row or not row[0]:
        bot.reply_to(message, "❌ شما در رابطه‌ای نیستید.")
        return

    pid = row[0]
    c.execute("UPDATE users SET partner_id = NULL WHERE user_id IN (?, ?)", (uid, pid))
    conn.commit()

    bot.send_message(
        message.chat.id,
        f"💔 رابطه بین @{get_username(uid)} و @{get_username(pid)} به پایان رسید... 😢"
    )

# —————————————————————————————————————————————
# COIN TRANSFER
@bot.message_handler(commands=['give'])
def give_coin(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ ریپلای روی پیام کسی که می‌خوای سکه بدی.")
        return
    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "❌ فرمت: /give 100")
        return
    amt = int(parts[1])
    sender = message.from_user.id
    receiver = message.reply_to_message.from_user.id

    c.execute("SELECT coin FROM users WHERE user_id = ?", (sender,))
    row = c.fetchone()
    if not row or row[0] < amt:
        bot.reply_to(message, "❌ سکه کافی نداری!")
        return

    c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (amt, sender))
    c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amt, receiver))
    conn.commit()
    bot.reply_to(message,
                 f"💸 @{message.from_user.username} تعداد {amt} سکه به @{get_username(receiver)} انتقال داد.")

# —————————————————————————————————————————————
# ADMIN MANAGEMENT
@bot.message_handler(commands=['admin'])
def add_bot_admin(message):
    if message.from_user.id != OWNER_ID:
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ ریپلای کنید روی پیام کسی که می‌خواید مدیر کنید.")
        return
    uid = message.reply_to_message.from_user.id
    c.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (uid,))
    conn.commit()
    bot.reply_to(message, f"✅ @{get_username(uid)} به مدیران ربات اضافه شد.")

@bot.message_handler(commands=['dadmin'])
def del_bot_admin(message):
    if message.from_user.id != OWNER_ID:
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ ریپلای کنید روی پیام کسی که می‌خواید از مدیران حذف کنید.")
        return
    uid = message.reply_to_message.from_user.id
    c.execute("UPDATE users SET is_admin = 0 WHERE user_id = ?", (uid,))
    conn.commit()
    bot.reply_to(message, f"❌ @{get_username(uid)} از مدیران ربات حذف شد.")

@bot.message_handler(commands=['ddadmin'])
def del_all_admins(message):
    if message.from_user.id != OWNER_ID:
        return
    c.execute("UPDATE users SET is_admin = 0")
    conn.commit()
    bot.reply_to(message, "👢 همه مدیران ربات حذف شدند.")

# —————————————————————————————————————————————
# SHOP / SPELLS
@bot.message_handler(commands=['shop'])
def show_shop(message):
    text = '''
🎁 فروشگاه طلسم‌ها:

1️⃣ 🧼 بپاک  (/del) – ۲۰ سکه  
2️⃣ 🧊 حبس یخی (/mut) – ۸۰ سکه
'''
    bot.reply_to(message, text)

@bot.message_handler(commands=['del'])
def delete_message(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ ریپلای کنید روی پیام.")
        return
    uid = message.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id = ?", (uid,))
    if c.fetchone()[0] < 20:
        bot.reply_to(message, "❌ سکه کافی نداری!")
        return
    try:
        bot.delete_message(message.chat.id, message.reply_to_message.message_id)
        c.execute("UPDATE users SET coin = coin - 20 WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "🧼 پیام حذف شد و ۲۰ سکه کسر شد.")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا: {e}")

@bot.message_handler(commands=['mut'])
def mute_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ ریپلای کنید روی پیام کاربر.")
        return
    uid = message.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id = ?", (uid,))
    if c.fetchone()[0] < 80:
        bot.reply_to(message, "❌ سکه کافی نداری!")
        return
    try:
        bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=message.reply_to_message.from_user.id,
            until_date=int(time.time()) + 60,
            can_send_messages=False
        )
        c.execute("UPDATE users SET coin = coin - 80 WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "🧊 کاربر سکوت شد و ۸۰ سکه کسر شد.")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا: {e}")

# —————————————————————————————————————————————
# GOLD TICK
@bot.message_handler(commands=['tik'])
def give_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        tid = message.reply_to_message.from_user.id
        c.execute("UPDATE users SET gold_tick = 1 WHERE user_id = ?", (tid,))
        conn.commit()
        bot.reply_to(message, "⚜️ نشان تایید طلایی داده شد ✅")

@bot.message_handler(commands=['dtik'])
def remove_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        tid = message.reply_to_message.from_user.id
        c.execute("UPDATE users SET gold_tick = 0 WHERE user_id = ?", (tid,))
        conn.commit()
        bot.reply_to(message, "❌ نشان تایید طلایی برداشته شد")

# —————————————————————————————————————————————
# OWNER CONTROLS: COIN / SCORE / ROLE
@bot.message_handler(func=lambda m: m.reply_to_message)
def control_points(message):
    if message.from_user.id not in (OWNER_ID,) and message.from_user.id not in [a[0] for a in c.execute("SELECT user_id FROM users WHERE is_admin=1")]:
        return

    uid = message.reply_to_message.from_user.id
    txt = message.text.strip()

    # سکه
    if re.match(r'^\+ 🪙 \d+$', txt):
        amt = int(txt.split()[-1])
        c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amt, uid))
        conn.commit()
        bot.reply_to(message, f"💰 {amt} سکه اضافه شد!")

    elif re.match(r'^\- 🪙 \d+$', txt):
        amt = int(txt.split()[-1])
        c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (amt, uid))
        conn.commit()
        bot.reply_to(message, f"💸 {amt} سکه کم شد!")

    # امتیاز
    elif re.match(r'^\+ \d+$', txt):
        amt = int(txt.split()[-1])
        c.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (amt, uid))
        conn.commit()
        bot.reply_to(message, f"🎉 {amt} امتیاز اضافه شد!")

    elif re.match(r'^\- \d+$', txt):
        amt = int(txt.split()[-1])
        c.execute("UPDATE users SET score = score - ? WHERE user_id = ?", (amt, uid))
        conn.commit()
        bot.reply_to(message, f"💔 {amt} امتیاز کم شد!")

    # مقام
    elif re.match(r'^\+m\d{1,2}$', txt):
        key = txt[1:]
        if key in ranks:
            c.execute("UPDATE users SET role = ? WHERE user_id = ?", (ranks[key], uid))
            conn.commit()
            bot.reply_to(message, f"👑 مقام {ranks[key]} ثبت شد!")

    elif re.match(r'^\-m\d{1,2}$', txt):
        c.execute("UPDATE users SET role = 'ممبر عادی 🧍' WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "🔻 مقام به پیش‌فرض برگشت.")

# —————————————————————————————————————————————
bot.infinity_polling()
