import telebot
from telebot import types
import sqlite3
import re
import time

TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
OWNER_ID = 7341748124
bot = telebot.TeleBot(TOKEN)

# حذف وب‌هوک قبلی برای جلوگیری از ارور 409
bot.remove_webhook()
time.sleep(1)

# اتصال به دیتابیس
conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

# ساخت جدول کاربران با ستون rank_code برای مقام
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    coin INTEGER DEFAULT 180,
    score INTEGER DEFAULT 250,
    gold_tick INTEGER DEFAULT 0,
    rank_code TEXT DEFAULT 'm10'
)
''')
conn.commit()

# دیکشنری مقام‌ها
ranks = {
    "m1": "سوگولی گروه",
    "m2": "پرنسس گروه",
    "m3": "ملکه گروه",
    "m4": "شوالیه گروه",
    "m5": "رهبر گروه",
    "m6": "اونر گروه",
    "m7": "زامبی الفا گروه",
    "m8": "نفس گروه",
    "m9": "بادیگارد گروه",
    "m10": "ممبر عادی"
}

# افزودن کاربر جدید
def add_user(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username if message.from_user.username else "ندارد"

    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)", (user_id, name, username))
        conn.commit()

# تابع درجه‌بندی بر اساس امتیاز
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

# دستور /my برای نمایش پروفایل
@bot.message_handler(commands=['my'])
def show_profile(message):
    add_user(message)
    user_id = message.from_user.id
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if data:
        tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"
        rank = get_rank(data[4])
        rank_code = data[6] if len(data) > 6 else "m10"
        rank_name = ranks.get(rank_code, "ممبر عادی")

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
🎂 تاریخ تولدت:
🔮 قدرت‌ها و طلسم‌ها:

:: در گروه :::::

▪︎🏆 درجه شما در گروه: {rank}
▪︎💠 مقام شما در گروه: {rank_name}
'''
        bot.reply_to(message, text)

# دستور /tik برای فعال‌سازی تیک طلایی
@bot.message_handler(commands=['tik'])
def give_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        uid = message.reply_to_message.from_user.id
        c.execute("UPDATE users SET gold_tick = 1 WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "⚜️ نشان تایید طلایی برای این کاربر فعال شد ✅")

# دستور /dtik برای حذف تیک طلایی
@bot.message_handler(commands=['dtik'])
def remove_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        uid = message.reply_to_message.from_user.id
        c.execute("UPDATE users SET gold_tick = 0 WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "❌ نشان تایید طلایی از این کاربر برداشته شد.")

# مدیریت سکه و امتیاز با ریپلای
@bot.message_handler(func=lambda m: m.reply_to_message)
def control_points(message):
    if message.from_user.id != OWNER_ID:
        return
    uid = message.reply_to_message.from_user.id
    text = message.text.strip()

    # افزودن سکه  
    if re.match(r'^\+ 🪙 \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💰 تعداد {amount} سکه به حساب <code>{uid}</code> اضافه شد!\n✨ ثروتت داره بیشتر میشه 😎", parse_mode="HTML")

    # کم کردن سکه  
    elif re.match(r'^\- 🪙 \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💸 تعداد {amount} سکه از حساب <code>{uid}</code> کم شد!\nمراقب باش که صفر نشی! 🫣", parse_mode="HTML")

    # افزودن امتیاز  
    elif re.match(r'^\+ \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"🎉 {amount} امتیاز به <code>{uid}</code> اضافه شد!\nدرخششت مبارک! 🌟", parse_mode="HTML")

    # کم کردن امتیاز  
    elif re.match(r'^\- \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET score = score - ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💔 {amount} امتیاز از <code>{uid}</code> کم شد!\nولی نگران نباش، جبران میشه! 💪", parse_mode="HTML")

    # مدیریت مقام‌ها
    elif re.match(r'^[\+\-]m\d+$', text):
        op = text[0]  # + یا -
        code = text[1:]  # مثلا m4

        print(f"[DEBUG] مدیریت مقام: عملیات={op}, کد={code}, آی‌دی کاربر={uid}")

        if code not in ranks:
            bot.reply_to(message, "⚠ کد مقام معتبر نیست.")
            print(f"[DEBUG] کد مقام نامعتبر: {code}")
            return

        c.execute("SELECT rank_code FROM users WHERE user_id = ?", (uid,))
        res = c.fetchone()
        current_code = res[0] if res else "m10"
        print(f"[DEBUG] مقام فعلی کاربر: {current_code}")

        if op == '+':
            if current_code == code:
                bot.reply_to(message, f"⚠ کاربر قبلاً مقام «{ranks[code]}» را دارد.")
                print(f"[DEBUG] کاربر قبلاً این مقام را دارد: {code}")
            else:
                c.execute("UPDATE users SET rank_code = ? WHERE user_id = ?", (code, uid))
                conn.commit()
                bot.reply_to(message, f"✔ مقام «{ranks[code]}» به کاربر داده شد.")
                print(f"[DEBUG] مقام داده شد: {code}")

        elif op == '-':
            if current_code == code:
                c.execute("UPDATE users SET rank_code = 'm10' WHERE user_id = ?", (uid,))
                conn.commit()
                bot.reply_to(message, f"✔ مقام «{ranks[code]}» از کاربر گرفته شد و به «ممبر عادی» برگشت.")
                print(f"[DEBUG] مقام گرفته شد: {code}")
            else:
                bot.reply_to(message, f"⚠ کاربر این مقام را ندارد.")
                print(f"[DEBUG] کاربر این مقام را ندارد: {code}")

# شروع ربات
bot.infinity_polling()
