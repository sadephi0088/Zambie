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

# اضافه کردن ستون مقام و تولد در صورت نیاز
# ستون birthdate فقط یکبار اضافه میشه؛ اگر خطا داد یعنی وجود داره و ردش کن
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
except Exception:
    # اگر جدول قبلاً بوده و ستون birthdate نبود، ستون رو اضافه کن
    try:
        c.execute("ALTER TABLE users ADD COLUMN birthdate TEXT")
        conn.commit()
    except:
        pass  # ستون وجود دارد، رد می‌کنیم

# دیکشنری مقام‌ها با ایموجی
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
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username if message.from_user.username else "ندارد"

    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)", (user_id, name, username))
        conn.commit()

def get_rank(score):
    if score < 500:
        return "تازه‌کار 👶"
    elif score < 1000:
        return "حرفه‌ای 🔥"
    elif score < 2000:
        return "استاد 🌟"
    elif score < 4000:
        return "قهرمان 🏆"
    elif score < 7000:
        return "افسانه‌ای 🐉"
    elif score < 10000:
        return "بی‌نظیر 💎"
    else:
        return "اسطوره 🚀"

@bot.message_handler(commands=['my'])
def show_profile(message):
    add_user(message)
    user_id = message.from_user.id
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if data:
        tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"
        rank = get_rank(data[4])
        role = data[6] if data[6] else "ممبر عادی 🧍"
        birthdate = data[7] if len(data) > 7 and data[7] else "ثبت نشده ❌"

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
😍 اسم همسر یا عشق‌ِت:
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
    user_id = message.from_user.id
    text = message.text.strip()
    
    match = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', text)
    if not match:
        bot.reply_to(message, "❌ فرمت تاریخ تولد اشتباه است. لطفاً به شکل زیر وارد کنید:\n/old 1379/1/11")
        return

    birthdate = match.group(1)

    c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if not data or data[0] < 40:
        bot.reply_to(message, "❌ سکه کافی برای ثبت تاریخ تولد نداری!")
        return

    # ثبت یا به‌روزرسانی تاریخ تولد
    c.execute("UPDATE users SET birthdate = ?, coin = coin - 40 WHERE user_id = ?", (birthdate, user_id))
    conn.commit()
    bot.reply_to(message, f"🎂 تاریخ تولد شما در پروفایلت ثبت شد و ۴۰ سکه از حسابت کسر گردید. 🎉")

# -- بقیه دستورات قبلی بدون تغییر --

@bot.message_handler(commands=['tik'])
def give_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        uid = message.reply_to_message.from_user.id
        c.execute("UPDATE users SET gold_tick = 1 WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "⚜️ نشان تایید طلایی برای این کاربر فعال شد ✅")

@bot.message_handler(commands=['dtik'])
def remove_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        uid = message.reply_to_message.from_user.id
        c.execute("UPDATE users SET gold_tick = 0 WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "❌ نشان تایید طلایی از این کاربر برداشته شد.")

@bot.message_handler(commands=['shop'])
def show_shop(message):
    text = '''
🎁 قدرت‌ها و طلسم‌های فعالت:

1️⃣ 🧼 طلسم بپاک  
   • دستور استفاده: ریپلای روی پیام + /del  
   • هزینه: ۲۰ سکه  
   • توضیح: پیام ریپلای‌شده را پاک می‌کنی، بی‌صدا و سریع!

2️⃣ 🧊 طلسم حبس یخی  
   • دستور استفاده: ریپلای روی کاربر + /mut  
   • هزینه: ۸۰ سکه  
   • توضیح: کاربر را برای ۶۰ ثانیه به حالت سکوت می‌بری!
'''
    bot.reply_to(message, text)

@bot.message_handler(commands=['del'])
def delete_message(message):
    if message.reply_to_message:
        user_id = message.from_user.id
        c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
        data = c.fetchone()
        if not data or data[0] < 20:
            bot.reply_to(message, "❌ سکه کافی برای اجرای طلسم بپاک نداری!")
            return
        try:
            bot.delete_message(message.chat.id, message.reply_to_message.message_id)
            c.execute("UPDATE users SET coin = coin - 20 WHERE user_id = ?", (user_id,))
            conn.commit()
            bot.reply_to(message, "🧼 پیام حذف شد و ۲۰ سکه از حساب شما کسر گردید.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا در حذف پیام: {str(e)}")
    else:
        bot.reply_to(message, "❌ برای اجرای دستور باید روی پیام ریپلای کنی.")

@bot.message_handler(commands=['mut'])
def mute_user(message):
    if message.reply_to_message:
        user_id = message.from_user.id
        c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
        data = c.fetchone()
        if not data or data[0] < 80:
            bot.reply_to(message, "❌ سکه کافی برای اجرای طلسم حبس یخی نداری!")
            return
        try:
            bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=message.reply_to_message.from_user.id,
                until_date=int(time.time()) + 60,
                can_send_messages=False
            )
            c.execute("UPDATE users SET coin = coin - 80 WHERE user_id = ?", (user_id,))
            conn.commit()
            bot.reply_to(message, "🧊 کاربر به مدت ۶۰ ثانیه سکوت شد و ۸۰ سکه از حساب شما کسر گردید.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا در اجرای طلسم حبس یخی: {str(e)}")
    else:
        bot.reply_to(message, "❌ برای اجرای دستور باید روی پیام کاربر مورد نظر ریپلای کنی.")

@bot.message_handler(func=lambda m: m.reply_to_message)
def control_points(message):
    if message.from_user.id != OWNER_ID:
        return

    uid = message.reply_to_message.from_user.id
    text = message.text.strip()

    # سکه
    if re.match(r'^\+ 🪙 \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💰 {amount} سکه به حساب {uid} اضافه شد!", parse_mode="HTML")

    elif re.match(r'^\- 🪙 \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💸 {amount} سکه از حساب {uid} کم شد!", parse_mode="HTML")

    # امتیاز
    elif re.match(r'^\+ \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"🎉 {amount} امتیاز اضافه شد!", parse_mode="HTML")

    elif re.match(r'^\- \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET score = score - ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💔 {amount} امتیاز کم شد!", parse_mode="HTML")

    # مقام اضافه کردن
    elif re.match(r'^\+m\d{1,2}$', text):
        key = text[1:]
        if key in ranks:
            c.execute("UPDATE users SET role = ? WHERE user_id = ?", (ranks[key], uid))
            conn.commit()
            bot.reply_to(message, f"👑 مقام جدید: <b>{ranks[key]}</b> برای کاربر ثبت شد!", parse_mode="HTML")

    # مقام حذف کردن
    elif re.match(r'^\-m\d{1,2}$', text):
        c.execute("UPDATE users SET role = 'ممبر عادی 🧍' WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "🔻 مقام کاربر حذف شد و به حالت پیش‌فرض برگشت.")

bot.infinity_polling()
