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

conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

# ایجاد جدول users با ستون‌های مورد نیاز
try:
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT,
        coin INTEGER DEFAULT 180,
        score INTEGER DEFAULT 250,
        gold_tick INTEGER DEFAULT 0,
        role TEXT DEFAULT 'ممبر عادی 🧍',
        birthdate TEXT,
        partner_id INTEGER
    )
    ''')
    conn.commit()
except:
    pass

# اگر ستون birthdate یا partner_id نبود، بهش اضافه می‌کنیم
for col in ("birthdate", "partner_id"):
    try:
        c.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
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
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username or "ندارد"
    c.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)",
                  (user_id, name, username))
        conn.commit()

def get_username(user_id):
    if not user_id:
        return "ندارد ❌"
    c.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    return row[0] if row else "ندارد ❌"

def get_rank(score):
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

# —————————————————————————————————————————
@bot.message_handler(commands=['start'])
def start_handler(message):
    add_user(message)
    text = f'''
سلام @{message.from_user.username} عزیز! 🌹
به ربات ما خوش اومدی.
برای دیدن پروفایلت /my
برای عشق بازی /love (ریپلای)
برای طلاق /dlove
برای فروشگاه /shop
برای لیست مقام‌ها /ranks
برای ثبت تولد /old
برای راهنما /help
'''
    bot.reply_to(message, text)

@bot.message_handler(commands=['help'])
def help_handler(message):
    text = '''
📖 راهنما:

/start      – خوش‌آمدگویی  
/my         – نمایش پروفایل  
/love       – درخواست عشق (ریپلای روی پیام)  
/dlove      – پایان رابطه  
/shop       – فروشگاه طلسم‌ها  
/old        – ثبت تاریخ تولد (۴۰ سکه)  
/ranks      – لیست مقام‌ها  
/tik        – اعطای نشان طلا (ادمین ریپلای)  
/dtik       – برداشتن نشان طلا (ادمین ریپلای)  
/del        – طلسم بپاک (ریپلای +۲۰ سکه)  
/mut        – طلسم حبس یخی (ریپلای +۸۰ سکه)  
'''
    bot.reply_to(message, text)

@bot.message_handler(commands=['ranks'])
def ranks_handler(message):
    text = "📜 مقام‌های گروه:\n"
    for key,val in ranks.items():
        text += f"{key} — {val}\n"
    bot.reply_to(message, text)

# —————————————————————————————————————————
@bot.message_handler(commands=['my'])
def show_profile(message):
    add_user(message)
    user_id = message.from_user.id
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
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
━━━【 پروفایل شما 】━━━

👤 نام: {data[1]}
✨ یوزرنیم: @{data[2]}
⚔️ آیدی: {data[0]}

💰 سکه: {data[3]}
💎 امتیاز: {data[4]}
⚜️ تایید طلایی: {tick}

😍 همسر/عشق: {partner_username}
🎂 تولد: {birthdate}

🏆 رتبه: {rank}
💠 مقام: {role}
'''
    bot.reply_to(message, text)

@bot.message_handler(commands=['old'])
def set_birthdate(message):
    user_id = message.from_user.id
    m = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', message.text.strip())
    if not m:
        bot.reply_to(message, "❌ فرمت نادرسته. مثال:\n/old 1379/1/11")
        return
    bd = m.group(1)
    c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row or row[0] < 40:
        bot.reply_to(message, "❌ سکه کافی نداری!")
        return
    c.execute("UPDATE users SET birthdate = ?, coin = coin - 40 WHERE user_id = ?",
              (bd, user_id))
    conn.commit()
    bot.reply_to(message, "🎂 تولد ثبت شد و ۴۰ سکه کسر گردید.")

# —————————————————————————————————————————
@bot.message_handler(commands=['love'])
def love_request(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ ریپلای روی پیام طرف مقابل.")
        return

    req = message.from_user
    tgt = message.reply_to_message.from_user
    if req.id == tgt.id:
        bot.reply_to(message, "❌ نمی‌تونی با خودت باشی!")
        return

    add_user(message)
    add_user(message.reply_to_message)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💖 قبول می‌کنم", callback_data=f"accept_{req.id}"),
        types.InlineKeyboardButton("💔 قبول نمی‌کنم", callback_data=f"reject_{req.id}")
    )

    txt = (f"🎯 @{tgt.username}\n"
           f"💌 @{req.username} عاشقته و می‌خواد باهات ازدواج کنه!\n\n"
           "آیا قبول می‌کنی؟ 😍")
    sent = bot.send_message(message.chat.id, txt, reply_markup=markup)
    pending_loves[sent.message_id] = req.id

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
            bot.edit_message_text("❌ درخواست‌کننده سکه کافی نداره!",
                                  call.message.chat.id, mid)
            del pending_loves[mid]
            return

        c.execute("UPDATE users SET partner_id = ? WHERE user_id = ?", (res_id, req_id))
        c.execute("UPDATE users SET partner_id = ? WHERE user_id = ?", (req_id, res_id))
        c.execute("UPDATE users SET coin = coin - 40 WHERE user_id = ?", (req_id,))
        conn.commit()

        bot.edit_message_text("💖 عشق پذیرفته شد! 🎉", call.message.chat.id, mid)
        bot.send_message(call.message.chat.id,
                         f"🎊 @{get_username(req_id)} و @{get_username(res_id)} حالا عاشق هم هستن! 💘")
    else:
        bot.edit_message_text("💔 عشق رد شد.", call.message.chat.id, mid)

    del pending_loves[mid]

# —————————————————————————————————————————
@bot.message_handler(commands=['dlove'])
def divorce_love(message):
    uid = message.from_user.id
    c.execute("SELECT partner_id FROM users WHERE user_id = ?", (uid,))
    row = c.fetchone()
    if not row or not row[0]:
        bot.reply_to(message, "❌ در رابطه نیستی.")
        return

    pid = row[0]
    c.execute("UPDATE users SET partner_id = NULL WHERE user_id IN (?, ?)", (uid, pid))
    conn.commit()

    bot.send_message(message.chat.id,
                     f"💔 رابطه بین @{get_username(uid)} و @{get_username(pid)} به پایان رسید... 😢")

# —————————————————————————————————————————
@bot.message_handler(commands=['shop'])
def show_shop(message):
    text = '''
🎁 طلسم‌ها:

1️⃣ 🧼 بپاک  (/del) – ۲۰ سکه  
2️⃣ 🧊 حبس یخی  (/mut) – ۸۰ سکه
'''
    bot.reply_to(message, text)

@bot.message_handler(commands=['del'])
def delete_message(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ ریپلای کن.")
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
        bot.reply_to(message, "🧼 حذف و ۲۰ سکه کسر شد.")
    except Exception as e:
        bot.reply_to(message, f"❌ {e}")

@bot.message_handler(commands=['mut'])
def mute_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ ریپلای کن.")
        return
    uid = message.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id = ?", (uid,))
    if c.fetchone()[0] < 80:
        bot.reply_to(message, "❌ سکه کافی نیست!")
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
        bot.reply_to(message, "🧊 سکوت و ۸۰ سکه کسر شد.")
    except Exception as e:
        bot.reply_to(message, f"❌ {e}")

@bot.message_handler(commands=['tik'])
def give_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        tid = message.reply_to_message.from_user.id
        c.execute("UPDATE users SET gold_tick = 1 WHERE user_id = ?", (tid,))
        conn.commit()
        bot.reply_to(message, "⚜️ تایید طلایی شد!")

@bot.message_handler(commands=['dtik'])
def remove_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        tid = message.reply_to_message.from_user.id
        c.execute("UPDATE users SET gold_tick = 0 WHERE user_id = ?", (tid,))
        conn.commit()
        bot.reply_to(message, "❌ تایید طلایی برداشته شد.")

@bot.message_handler(func=lambda m: m.reply_to_message)
def control_points(message):
    if message.from_user.id != OWNER_ID:
        return
    uid = message.reply_to_message.from_user.id
    txt = message.text.strip()

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

    elif re.match(r'^\+m\d{1,2}$', txt):
        key = txt[1:]
        if key in ranks:
            c.execute("UPDATE users SET role = ? WHERE user_id = ?", (ranks[key], uid))
            conn.commit()
            bot.reply_to(message, f"👑 مقام {ranks[key]} ثبت شد!")

    elif re.match(r'^\-m\d{1,2}$', txt):
        c.execute("UPDATE users SET role = 'ممبر عادی 🧍' WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "🔻 برگشت به پیش‌فرض.")

bot.infinity_polling()
