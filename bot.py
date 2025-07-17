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

# ساخت جدول users اگر وجود نداشته باشد
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
        blocked INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
except Exception:
    pass

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

admins = set()  # ادمین‌های ربات

def add_user(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username if message.from_user.username else "ندارد"
    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)", (user_id, name, username))
        conn.commit()

def user_blocked(user_id):
    c.execute("SELECT blocked FROM users WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    return res and res[0] == 1

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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    add_user(message)
    bot.reply_to(message, "سلام! خوش آمدی به ربات ❤️")

@bot.message_handler(commands=['my'])
def show_profile(message):
    add_user(message)
    user_id = message.from_user.id
    if user_blocked(user_id):
        bot.reply_to(message, "⚠️ شما محدود شده‌اید و نمی‌توانید از این دستور استفاده کنید.")
        return

    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if data:
        tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"
        rank = get_rank(data[4])
        role = data[6] if data[6] else "ممبر عادی 🧍"
        birthdate = data[7] if data[7] else "ثبت نشده ❌"

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
    if user_blocked(user_id):
        bot.reply_to(message, "⚠️ شما محدود شده‌اید و نمی‌توانید از این دستور استفاده کنید.")
        return

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

    c.execute("UPDATE users SET birthdate = ?, coin = coin - 40 WHERE user_id = ?", (birthdate, user_id))
    conn.commit()
    bot.reply_to(message, f"🎂 تاریخ تولد شما ثبت شد و ۴۰ سکه از حسابت کسر گردید. 🎉")

@bot.message_handler(commands=['tik'])
def give_tick(message):
    if message.from_user.id != OWNER_ID:
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ برای دادن نشان، روی پیام کاربر ریپلای کن.")
        return
    uid = message.reply_to_message.from_user.id
    c.execute("UPDATE users SET gold_tick = 1 WHERE user_id = ?", (uid,))
    conn.commit()
    bot.reply_to(message, "⚜️ نشان تایید طلایی فعال شد ✅")

@bot.message_handler(commands=['dtik'])
def remove_tick(message):
    if message.from_user.id != OWNER_ID:
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ برای برداشتن نشان، روی پیام کاربر ریپلای کن.")
        return
    uid = message.reply_to_message.from_user.id
    c.execute("UPDATE users SET gold_tick = 0 WHERE user_id = ?", (uid,))
    conn.commit()
    bot.reply_to(message, "❌ نشان تایید طلایی برداشته شد.")

@bot.message_handler(commands=['shop'])
def show_shop(message):
    if user_blocked(message.from_user.id):
        bot.reply_to(message, "⚠️ شما محدود شده‌اید و نمی‌توانید از این دستور استفاده کنید.")
        return
    text = '''
🎁 قدرت‌ها و طلسم‌های فعالت:

1️⃣ 🧼 طلسم بپاک  
   • دستور: ریپلای روی پیام + /del  
   • هزینه: ۲۰ سکه  
   • توضیح: پیام ریپلای‌شده را پاک می‌کند!

2️⃣ 🧊 طلسم حبس یخی  
   • دستور: ریپلای روی کاربر + /mut  
   • هزینه: ۸۰ سکه  
   • توضیح: سکوت ۶۰ ثانیه‌ای برای کاربر!
'''
    bot.reply_to(message, text)

@bot.message_handler(commands=['del'])
def delete_message(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ باید روی پیام ریپلای کنی.")
        return
    user_id = message.from_user.id
    if user_blocked(user_id):
        bot.reply_to(message, "⚠️ شما محدود شده‌اید و نمی‌توانید از این دستور استفاده کنید.")
        return

    c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if not data or data[0] < 20:
        bot.reply_to(message, "❌ سکه کافی نداری!")
        return
    try:
        bot.delete_message(message.chat.id, message.reply_to_message.message_id)
        c.execute("UPDATE users SET coin = coin - 20 WHERE user_id = ?", (user_id,))
        conn.commit()
        bot.reply_to(message, "🧼 پیام حذف شد و ۲۰ سکه کم شد.")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا: {str(e)}")

@bot.message_handler(commands=['mut'])
def mute_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ باید روی پیام کاربر ریپلای کنی.")
        return
    user_id = message.from_user.id
    if user_blocked(user_id):
        bot.reply_to(message, "⚠️ شما محدود شده‌اید و نمی‌توانید از این دستور استفاده کنید.")
        return
    c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if not data or data[0] < 80:
        bot.reply_to(message, "❌ سکه کافی نداری!")
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
        bot.reply_to(message, "🧊 کاربر ۶۰ ثانیه سکوت شد و ۸۰ سکه کم شد.")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا: {str(e)}")

@bot.message_handler(func=lambda m: m.reply_to_message)
def control_points(message):
    if message.from_user.id != OWNER_ID and message.from_user.id not in admins:
        return
    uid = message.reply_to_message.from_user.id
    text = message.text.strip()

    # اضافه کردن سکه
    if re.match(r'^\+ 🪙 \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💰 {amount} سکه اضافه شد!")

    # کم کردن سکه
    elif re.match(r'^\- 🪙 \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💸 {amount} سکه کم شد!")

    # اضافه کردن امتیاز
    elif re.match(r'^\+ \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"🎉 {amount} امتیاز اضافه شد!")

    # کم کردن امتیاز
    elif re.match(r'^\- \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET score = score - ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💔 {amount} امتیاز کم شد!")

    # دادن مقام
    elif re.match(r'^\+m\d{1,2}$', text):
        key = text[1:]
        if key in ranks:
            c.execute("UPDATE users SET role = ? WHERE user_id = ?", (ranks[key], uid))
            conn.commit()
            bot.reply_to(message, f"👑 مقام {ranks[key]} ثبت شد!")

    # حذف مقام
    elif re.match(r'^\-m\d{1,2}$', text):
        c.execute("UPDATE users SET role = 'ممبر عادی 🧍' WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "🔻 مقام حذف شد.")

# مدیریت ادمین‌ها

@bot.message_handler(commands=['admin'])
def add_admin(message):
    if message.from_user.id != OWNER_ID:
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ روی پیام کاربر ریپلای کن.")
        return
    uid = message.reply_to_message.from_user.id
    admins.add(uid)
    bot.reply_to(message, f"👑 کاربر {uid} ادمین شد.")

@bot.message_handler(commands=['dadmin'])
def del_admin(message):
    if message.from_user.id != OWNER_ID:
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ روی پیام کاربر ریپلای کن.")
        return
    uid = message.reply_to_message.from_user.id
    if uid in admins:
        admins.remove(uid)
        bot.reply_to(message, f"❌ کاربر {uid} از ادمین‌ها حذف شد.")
    else:
        bot.reply_to(message, "❌ این کاربر ادمین نیست.")

# تعلیق و رفع تعلیق کاربران

@bot.message_handler(commands=['block'])
def block_user(message):
    if message.from_user.id != OWNER_ID and message.from_user.id not in admins:
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ روی پیام کاربر ریپلای کن.")
        return
    uid = message.reply_to_message.from_user.id
    c.execute("UPDATE users SET blocked = 1 WHERE user_id = ?", (uid,))
    conn.commit()
    bot.reply_to(message, f"⛔️ کاربر {uid} تعلیق شد.")

@bot.message_handler(commands=['unblock'])
def unblock_user(message):
    if message.from_user.id != OWNER_ID and message.from_user.id not in admins:
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ روی پیام کاربر ریپلای کن.")
        return
    uid = message.reply_to_message.from_user.id
    c.execute("UPDATE users SET blocked = 0 WHERE user_id = ?", (uid,))
    conn.commit()
    bot.reply_to(message, f"✅ کاربر {uid} رفع تعلیق شد.")

# شمارش پیام‌ها و پاداش

counting_active = {}
message_count = {}

@bot.message_handler(commands=['on'])
def start_counting(message):
    if message.from_user.id != OWNER_ID and message.from_user.id not in admins:
        return
    chat_id = message.chat.id
    counting_active[chat_id] = True
    message_count[chat_id] = {}
    bot.reply_to(message, "🎉 شمارش پیام‌ها فعال شد! هر ۵۰ پیام، هدیه می‌گیری!")

@bot.message_handler(commands=['off'])
def stop_counting(message):
    if message.from_user.id != OWNER_ID and message.from_user.id not in admins:
        return
    chat_id = message.chat.id
    counting_active[chat_id] = False
    bot.reply_to(message, "🔕 شمارش پیام‌ها متوقف شد.")

@bot.message_handler(func=lambda m: True)
def count_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_blocked(user_id):
        return
    if not counting_active.get(chat_id, False):
        return
    if chat_id not in message_count:
        message_count[chat_id] = {}
    if user_id not in message_count[chat_id]:
        message_count[chat_id][user_id] = 0
    message_count[chat_id][user_id] += 1
    if message_count[chat_id][user_id] % 50 == 0:
        c.execute("SELECT coin, score FROM users WHERE user_id = ?", (user_id,))
        data = c.fetchone()
        if data:
            new_coin = data[0] + 100
            new_score = data[1] + 50
            c.execute("UPDATE users SET coin = ?, score = ? WHERE user_id = ?", (new_coin, new_score, user_id))
            conn.commit()
            bot.send_message(chat_id, f"🎉 تبریک {message.from_user.first_name}! ۵۰ پیام نوشتی و ۱۰۰ سکه و ۵۰ امتیاز بردی!")

# اضافه کردن یوزر هنگام هر پیام
@bot.message_handler(func=lambda message: True)
def add_user_on_message(message):
    add_user(message)

bot.infinity_polling()
