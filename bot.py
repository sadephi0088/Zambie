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
😍 اسم همسر یا عشق‌ِت:
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

bot.infinity_polling()
