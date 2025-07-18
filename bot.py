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

# ساخت جدول یا اضافه کردن ستون‌ها
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
        love_name TEXT DEFAULT '-',
        love_username TEXT DEFAULT '-',
        love_request_from INTEGER DEFAULT NULL
    )
    ''')
    conn.commit()
except Exception:
    try:
        c.execute("ALTER TABLE users ADD COLUMN birthdate TEXT")
        c.execute("ALTER TABLE users ADD COLUMN love_name TEXT DEFAULT '-'")
        c.execute("ALTER TABLE users ADD COLUMN love_username TEXT DEFAULT '-'")
        c.execute("ALTER TABLE users ADD COLUMN love_request_from INTEGER DEFAULT NULL")
        conn.commit()
    except:
        pass

# دیکشنری مقام‌ها با ایموجی (همون قبلی)
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
        love_name = data[8] if data[8] and data[8] != "-" else "ندارد ❌"
        love_username = data[9] if data[9] and data[9] != "-" else "ندارد ❌"

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
😍 اسم همسر یا عشق‌ِت: {love_name}
✨ یوزرنیم همسر: @{love_username}
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

# دستور ثبت تاریخ تولد و دستورات قبلی بدون تغییر ...

@bot.message_handler(commands=['love'])
def love_cmd(message):
    if not message.reply_to_message:
        bot.reply_to(message, "برای ازدواج باید به پیام کسی ریپلای کنی 😍")
        return

    lover_id = message.reply_to_message.from_user.id
    user_id = message.from_user.id

    if lover_id == user_id:
        bot.reply_to(message, "با خودت که نمی‌تونی ازدواج کنی عزیز دلم 😅")
        return

    add_user(message)  # مطمئن شو هر دو طرف ثبت شده‌اند
    add_user(message.reply_to_message)

    c.execute("SELECT coin, love_name, love_request_from FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()

    if not result:
        bot.reply_to(message, "اول با یه پیام دیگه فرم بساز بعد دوباره تلاش کن 🌸")
        return

    coin, love_name, love_request_from = result
    if coin < 40:
        bot.reply_to(message, "برای ازدواج باید ۴۰ سکه داشته باشی 💰")
        return

    if love_name != "-" and love_name != "":
        bot.reply_to(message, "تو قبلاً ازدواج کردی عزیزم 💞")
        return

    # بررسی اینکه اگر قبلا درخواست ازدواج فرستاده شده
    if love_request_from == lover_id:
        bot.reply_to(message, "درخواست ازدواج قبلاً ارسال شده و منتظر جواب هستی 💌")
        return

    # ثبت درخواست ازدواج (فقط در user که درخواست رو فرستاده)
    c.execute("UPDATE users SET love_request_from = ? WHERE user_id = ?", (lover_id, user_id))
    conn.commit()

    # ارسال پیام درخواست ازدواج به طرف مقابل
    lover_name = message.reply_to_message.from_user.first_name
    bot.send_message(lover_id,
                     f"👰💍 کاربر {message.from_user.first_name} ازت درخواست ازدواج داده!\n"
                     f"اگر قبول داری /accept و اگر رد می‌کنی /reject بفرست.")

    bot.reply_to(message, f"درخواست ازدواج به {lover_name} ارسال شد. منتظر جواب باش 💌")

@bot.message_handler(commands=['accept'])
def accept_cmd(message):
    user_id = message.from_user.id

    c.execute("SELECT love_request_from FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if not result:
        bot.reply_to(message, "تو درخواستی برای قبول کردن نداری 😕")
        return

    lover_id = result[0]
    if lover_id is None:
        bot.reply_to(message, "درخواستی برای قبول کردن نداری 😕")
        return

    # چک کن اگر خودت ازدواج کرده‌ای
    c.execute("SELECT love_name FROM users WHERE user_id=?", (user_id,))
    love_name = c.fetchone()[0]
    if love_name != "-" and love_name != "":
        bot.reply_to(message, "تو قبلاً ازدواج کردی عزیزم 💞")
        return

    # چک کن طرف مقابل هم فرم داره
    c.execute("SELECT name, username, coin, love_name FROM users WHERE user_id=?", (lover_id,))
    lover_data = c.fetchone()
    if not lover_data:
        bot.reply_to(message, "طرف مقابل هنوز فرم نداره، پس نمیشه ازدواج کرد ✨")
        return

    # چک کن تو هم سکه کافی داری
    c.execute("SELECT coin FROM users WHERE user_id=?", (user_id,))
    coin_data = c.fetchone()
    if not coin_data or coin_data[0] < 40:
        bot.reply_to(message, "برای قبول ازدواج باید ۴۰ سکه داشته باشی 💰")
        return

    if lover_data[3] != "-" and lover_data[3] != "":
        bot.reply_to(message, "طرف مقابل قبلاً ازدواج کرده 😕")
        return

    # حالا ازدواج رو ثبت کن
    user_name = message.from_user.first_name
    user_username = message.from_user.username if message.from_user.username else "ندارد"
    lover_name = lover_data[0]
    lover_username = lover_data[1] if lover_data[1] else "ندارد"

    # ثبت در دیتابیس
    c.execute("UPDATE users SET love_name=?, love_username=?, coin = coin - 40, love_request_from=NULL WHERE user_id=?",
              (lover_name, lover_username, user_id))
    c.execute("UPDATE users SET love_name=?, love_username=? WHERE user_id=?",
              (user_name, user_username, lover_id))
    conn.commit()

    bot.reply_to(message, f"🎉 تبریک! {user_name} و {lover_name} با هم ازدواج کردن!\nاز این به بعد توی فرم‌هاتون ❤️ همسر ثبت می‌شه.")

@bot.message_handler(commands=['reject'])
def reject_cmd(message):
    user_id = message.from_user.id

    c.execute("SELECT love_request_from FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if not result or result[0] is None:
        bot.reply_to(message, "درخواستی برای رد کردن نداری 😕")
        return

    c.execute("UPDATE users SET love_request_from=NULL WHERE user_id=?", (user_id,))
    conn.commit()
    bot.reply_to(message, "درخواست ازدواج رد شد. 😔")

@bot.message_handler(commands=['dlove'])
def dlove_cmd(message):
    user_id = message.from_user.id

    c.execute("SELECT love_name FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if not result:
        bot.reply_to(message, "فرمی نداری که بخوای طلاق بگیری 😕")
        return

    partner_name = result[0]
    if partner_name == "-" or partner_name == "":
        bot.reply_to(message, "تو در حال حاضر در رابطه نیستی 😢")
        return

    # پیدا کردن آیدی همسر
    c.execute("SELECT user_id FROM users WHERE love_name=?", (message.from_user.first_name,))
    partner = c.fetchone()

    # پاک کردن اسم و یوزرنیم از هر دو طرف
    c.execute("UPDATE users SET love_name='-', love_username='-' WHERE user_id=?", (user_id,))
    if partner:
        c.execute("UPDATE users SET love_name='-', love_username='-' WHERE user_id=?", (partner[0],))
    conn.commit()

    bot.reply_to(message, f"💔 متاسفانه رابطه‌ی تو با {partner_name} به پایان رسید... طلاق ثبت شد.")

# ادامه دستورات و تابع add_user و ... (مثلاً /old، /tik و غیره) بدون تغییر

bot.infinity_polling()
