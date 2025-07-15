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

# ساخت جدول کاربران
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
        birthdate TEXT
    )
    ''')
    conn.commit()
except:
    pass

# جدول عشق/همسر
try:
    c.execute('''
    CREATE TABLE IF NOT EXISTS love (
        user_id INTEGER PRIMARY KEY,
        partner_id INTEGER,
        request_time INTEGER
    )
    ''')
    conn.commit()
except:
    pass

# لیست مقام‌ها
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

def add_user(message):
    uid = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username or "ندارد"
    c.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,))
    if not c.fetchone():
        with conn:
            c.execute("INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)", (uid, name, username))

def get_rank(score):
    if score < 500: return "تازه‌کار 👶"
    elif score < 1000: return "حرفه‌ای 🔥"
    elif score < 2000: return "استاد 🌟"
    elif score < 4000: return "قهرمان 🏆"
    elif score < 7000: return "افسانه‌ای 🐉"
    elif score < 10000: return "بی‌نظیر 💎"
    return "اسطوره 🚀"

def update_coin(uid, amount):
    with conn:
        c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amount, uid))

def update_score(uid, amount):
    with conn:
        c.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (amount, uid))

@bot.message_handler(commands=['my'])
def show_profile(message):
    add_user(message)
    uid = message.from_user.id
    c.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    data = c.fetchone()

    # دریافت همسر
    c.execute("SELECT partner_id FROM love WHERE user_id = ?", (uid,))
    partner_row = c.fetchone()
    if partner_row and partner_row[0]:
        partner_id = partner_row[0]
        c.execute("SELECT name, username FROM users WHERE user_id = ?", (partner_id,))
        p = c.fetchone()
        partner_text = f"{p[0]} (@{p[1]})" if p else "نامشخص"
    else:
        partner_text = "ندارد"

    if data:
        tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"
        rank = get_rank(data[4])
        role = data[6] or "ممبر عادی 🧍"
        birthdate = data[7] if data[7] else "ثبت نشده ❌"
        text = f'''
━━━【 پروفایل شما در گروه 】━━━

•مشخصات فردی شما•
👤 نام: {data[1]}
✨ یوزرنیم: @{data[2]}
⚔️ آیدی عددی: {data[0]}
🌐 کشور شما: 🇮🇷 ایران

• دارایی‌ها و امتیازت •
💰 سکه‌هات: {data[3]}
💎 امتیازت: {data[4]}
⚜️ نشان تایید طلایی: {tick}

•مشخصات خانواده شما•
😍 اسم همسر یا عشق‌ِت: {partner_text}
♥️ اسم فرزندتون:
🐣 حیوان خانگی شما:
♨️ فرقه‌ای که توش عضوی:
🌙 شکلک اختصاصی:
🎂 تاریخ تولدت: {birthdate}
🔮 قدرت‌ها و طلسم‌ها: (دستور /shop)

▪︎🏆 درجه شما در گروه: {rank}
▪︎💠 مقام شما در گروه: {role}
'''
        bot.reply_to(message, text)

@bot.message_handler(commands=['old'])
def set_birthdate(message):
    uid = message.from_user.id
    match = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', message.text.strip())
    if not match:
        return bot.reply_to(message, "❌ فرمت اشتباهه. مثال درست: /old 1380/5/10")
    
    birth = match.group(1)
    c.execute("SELECT coin FROM users WHERE user_id = ?", (uid,))
    data = c.fetchone()
    if not data or data[0] < 40:
        return bot.reply_to(message, "❌ سکه کافی برای ثبت تولد نداری!")
    
    with conn:
        c.execute("UPDATE users SET birthdate = ?, coin = coin - 40 WHERE user_id = ?", (birth, uid))
    bot.reply_to(message, f"🎂 تولدت ثبت شد و ۴۰ سکه کم شد.")

@bot.message_handler(commands=['tik'])
def give_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        uid = message.reply_to_message.from_user.id
        with conn:
            c.execute("UPDATE users SET gold_tick = 1 WHERE user_id = ?", (uid,))
        bot.reply_to(message, "⚜️ تیک طلایی فعال شد ✅")

@bot.message_handler(commands=['dtik'])
def remove_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        uid = message.reply_to_message.from_user.id
        with conn:
            c.execute("UPDATE users SET gold_tick = 0 WHERE user_id = ?", (uid,))
        bot.reply_to(message, "❌ تیک طلایی غیرفعال شد.")

@bot.message_handler(commands=['shop'])
def show_shop(message):
    text = '''
🎁 قدرت‌ها و طلسم‌های فعالت:

1️⃣ 🧼 طلسم بپاک  
   • ریپلای کن و بزن: /del  
   • هزینه: ۲۰ سکه  

2️⃣ 🧊 طلسم حبس یخی  
   • ریپلای کن و بزن: /mut  
   • هزینه: ۸۰ سکه  
'''
    bot.reply_to(message, text)

@bot.message_handler(commands=['del'])
def delete_message(message):
    if not message.reply_to_message:
        return bot.reply_to(message, "❌ باید روی پیام ریپلای کنی.")
    
    uid = message.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id = ?", (uid,))
    data = c.fetchone()
    if not data or data[0] < 20:
        return bot.reply_to(message, "❌ سکه کافی نداری!")

    try:
        bot.delete_message(message.chat.id, message.reply_to_message.message_id)
        update_coin(uid, -20)
        bot.reply_to(message, "🧼 پیام پاک شد و ۲۰ سکه کم شد.")
    except Exception as e:
        bot.reply_to(message, f"خطا: {str(e)}")

@bot.message_handler(commands=['mut'])
def mute_user(message):
    if not message.reply_to_message:
        return bot.reply_to(message, "❌ باید روی کاربر ریپلای کنی.")
    
    uid = message.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id = ?", (uid,))
    data = c.fetchone()
    if not data or data[0] < 80:
        return bot.reply_to(message, "❌ سکه کافی نداری!")

    try:
        bot.restrict_chat_member(
            message.chat.id,
            message.reply_to_message.from_user.id,
            until_date=int(time.time()) + 60,
            can_send_messages=False
        )
        update_coin(uid, -80)
        bot.reply_to(message, "🧊 کاربر به مدت ۶۰ ثانیه ساکت شد.")
    except Exception as e:
        bot.reply_to(message, f"خطا: {str(e)}")

@bot.message_handler(commands=['give'])
def gift_coin(message):
    if not message.reply_to_message:
        return bot.reply_to(message, "❌ باید روی پیام کسی که می‌خوای سکه بدی ریپلای کنی.")

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        return bot.reply_to(message, "❌ فرمت اشتباهه. مثال درست:\n/give 50")

    amount = int(args[1])
    if amount <= 0:
        return bot.reply_to(message, "❌ عدد باید مثبت باشه.")

    from_id = message.from_user.id
    to_user = message.reply_to_message.from_user
    to_id = to_user.id

    if from_id == to_id:
        return bot.reply_to(message, "😅 نمی‌تونی به خودت سکه بدی!")

    c.execute("SELECT coin FROM users WHERE user_id = ?", (from_id,))
    sender = c.fetchone()
    if not sender or sender[0] < amount:
        return bot.reply_to(message, "❌ سکه کافی نداری!")

    with conn:
        c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (amount, from_id))
        c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amount, to_id))

    bot.reply_to(message, f"🎁 {amount} سکه با موفقیت به 👤 <b>{to_user.first_name}</b> (🆔 {to_id}) واریز شد!", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.reply_to_message and m.from_user.id == OWNER_ID)
def control_points(message):
    uid = message.reply_to_message.from_user.id
    text = message.text.strip()

    if match := re.match(r'^\+ 🪙 (\d+)$', text):
        amount = int(match.group(1))
        update_coin(uid, amount)
        bot.reply_to(message, f"💰 {amount} سکه اضافه شد.")

    elif match := re.match(r'^\- 🪙 (\d+)$', text):
        amount = -int(match.group(1))
        update_coin(uid, amount)
        bot.reply_to(message, f"💸 {abs(amount)} سکه کم شد.")

    elif match := re.match(r'^\+ (\d+)$', text):
        amount = int(match.group(1))
        update_score(uid, amount)
        bot.reply_to(message, f"🎉 {amount} امتیاز اضافه شد.")

    elif match := re.match(r'^\- (\d+)$', text):
        amount = -int(match.group(1))
        update_score(uid, amount)
        bot.reply_to(message, f"💔 {abs(amount)} امتیاز کم شد.")

    elif match := re.match(r'^\+m(\d{1,2})$', text):
        key = f"m{match.group(1)}"
        if key in ranks:
            with conn:
                c.execute("UPDATE users SET role = ? WHERE user_id = ?", (ranks[key], uid))
            bot.reply_to(message, f"👑 مقام جدید: {ranks[key]}")

    elif re.match(r'^\-m\d{1,2}$', text):
        with conn:
            c.execute("UPDATE users SET role = 'ممبر عادی 🧍' WHERE user_id = ?", (uid,))
        bot.reply_to(message, "🔻 مقام کاربر حذف شد.")

# ========== بخش عشق و ازدواج ==========

# ارسال درخواست عشق /love (ریپلای روی پیام فرد)
@bot.message_handler(commands=['love'])
def love_request(message):
    if not message.reply_to_message:
        return bot.reply_to(message, "❌ لطفا درخواست رو با ریپلای روی پیام کسی که دوست داری ارسال کن.")
    from_id = message.from_user.id
    to_user = message.reply_to_message.from_user
    to_id = to_user.id

    if from_id == to_id:
        return bot.reply_to(message, "😅 نمی‌تونی به خودت درخواست بدی!")
    
    # بررسی ازدواج قبلی درخواست‌دهنده
    c.execute("SELECT partner_id FROM love WHERE user_id = ?", (from_id,))
    row = c.fetchone()
    if row and row[0]:
        bot.reply_to(message, f"❗ شما قبلا ازدواج کردی! اگر میخوای با {to_user.first_name} ازدواج کنی، اول باید طلاق بگیری.")
        return

    # ذخیره درخواست با زمان فعلی
    now = int(time.time())
    with conn:
        c.execute("INSERT OR REPLACE INTO love (user_id, partner_id, request_time) VALUES (?, ?, ?)", (from_id, to_id, now))

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("✅ قبول /setlove", callback_data=f"accept_love_{from_id}"),
        types.InlineKeyboardButton("❌ رد /dislove", callback_data=f"reject_love_{from_id}")
    )
    bot.reply_to(message, f"💌 <b>{message.from_user.first_name}</b> (@{message.from_user.username or 'ندارد'}) به <b>{to_user.first_name}</b> (@{to_user.username or 'ندارد'}) درخواست عشق داده!\n\nنفر مقابل با دستور /setlove قبول و با /dislove رد کن.", reply_markup=keyboard, parse_mode="HTML")

# قبول درخواست عشق /setlove
@bot.message_handler(commands=['setlove'])
def accept_love(message):
    from_id = message.from_user.id
    # پیدا کردن درخواستی که برای این نفر ارسال شده
    c.execute("SELECT user_id, request_time FROM love WHERE partner_id = ?", (from_id,))
    row = c.fetchone()
    if not row:
        return bot.reply_to(message, "❌ درخواستی برای قبول کردن پیدا نشد.")
    lover_id, request_time = row
    now = int(time.time())
    if now - request_time > 180:  # 3 دقیقه
        with conn:
            c.execute("DELETE FROM love WHERE user_id = ?", (lover_id,))
        return bot.reply_to(message, "⏳ زمان درخواست ازدواج تمام شده است.")
    
    # ثبت همسری دو طرفه
    with conn:
        c.execute("INSERT OR REPLACE INTO love (user_id, partner_id, request_time) VALUES (?, ?, ?)", (lover_id, from_id, now))
        c.execute("INSERT OR REPLACE INTO love (user_id, partner_id, request_time) VALUES (?, ?, ?)", (from_id, lover_id, now))
    
    bot.reply_to(message, f"💖 <b>{message.from_user.first_name}</b> و <b>{lover_id}</b> حالا عاشق هم هستند! ❤️‍🔥", parse_mode="HTML")

# رد درخواست عشق /dislove
@bot.message_handler(commands=['dislove'])
def reject_love(message):
    from_id = message.from_user.id
    c.execute("SELECT user_id FROM love WHERE partner_id = ?", (from_id,))
    row = c.fetchone()
    if not row:
        return bot.reply_to(message, "❌ درخواستی برای رد کردن پیدا نشد.")
    lover_id = row[0]
    with conn:
        c.execute("DELETE FROM love WHERE user_id = ?", (lover_id,))
    bot.reply_to(message, "💔 درخواست عشق رد شد.")

# طلاق /ddislove (در گروه توسط یکی از زوجین)
@bot.message_handler(commands=['ddislove'])
def divorce(message):
    user_id = message.from_user.id
    c.execute("SELECT partner_id FROM love WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row or not row[0]:
        return bot.reply_to(message, "❌ شما ازدواج نکردی که طلاق بگیری.")
    partner_id = row[0]

    with conn:
        c.execute("DELETE FROM love WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM love WHERE user_id = ?", (partner_id,))

    bot.send_message(message.chat.id, f"💔 <a href='tg://user?id={user_id}'>شما</a> و <a href='tg://user?id={partner_id}'>همسرتون</a> از هم جدا شدید...", parse_mode="HTML")


bot.infinity_polling()
