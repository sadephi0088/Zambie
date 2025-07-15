import telebot
from telebot import types
import sqlite3
import re
import time
import threading

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

# ساخت جدول lovers برای ثبت عشق
try:
    c.execute('''
    CREATE TABLE IF NOT EXISTS lovers (
        user1 INTEGER PRIMARY KEY,
        user2 INTEGER
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
        # اضافه کردن اسم و یوزرنیم عشق در پروفایل
        c.execute("SELECT user2 FROM lovers WHERE user1 = ?", (uid,))
        lover = c.fetchone()
        if lover:
            lover_id = lover[0]
            c.execute("SELECT name, username FROM users WHERE user_id = ?", (lover_id,))
            lover_data = c.fetchone()
            lover_name = lover_data[0] if lover_data else "ناشناس"
            lover_username = lover_data[1] or "ندارد"
            lover_text = f"{lover_name} (@{lover_username})"
        else:
            lover_text = "ثبت نشده ❌"

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
😍 اسم همسر یا عشق‌ِت: {lover_text}
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

pending_love_requests = {}  # نگه داشتن درخواست‌های عشق {user2_id: (user1_id, time)}

def remove_pending_request(user2_id):
    if user2_id in pending_love_requests:
        del pending_love_requests[user2_id]

@bot.message_handler(commands=['love'])
def send_love_request(message):
    if not message.reply_to_message:
        return bot.reply_to(message, "❌ باید روی پیام کسی که دوست داری ریپلای کنی و /love بزنی.")
    user1 = message.from_user
    user2 = message.reply_to_message.from_user

    if user1.id == user2.id:
        return bot.reply_to(message, "😅 نمی‌تونی به خودت عشق بدی!")

    # ثبت اولیه کاربران
    add_user(message)
    add_user(message.reply_to_message)

    # چک عشق قبلی
    c.execute("SELECT user2 FROM lovers WHERE user1 = ?", (user1.id,))
    if c.fetchone():
        return bot.reply_to(message, "❌ تو قبلاً عشق داری، اول طلاق بگیر!")

    c.execute("SELECT user2 FROM lovers WHERE user1 = ?", (user2.id,))
    if c.fetchone():
        return bot.reply_to(message, f"❌ {user2.first_name} قبلاً عشق داره، نمی‌تونی درخواست بدی!")

    # اگر قبلاً درخواست بود، حذفش کنیم
    if user2.id in pending_love_requests:
        del pending_love_requests[user2.id]

    # ذخیره درخواست و زمان
    pending_love_requests[user2.id] = (user1.id, time.time())

    text = f"""
💖 درخواست عشق از طرف {user1.first_name} ([@{user1.username or 'ندارد'}]) به {user2.first_name} رسید!

برای قبول کردن، فقط کافیست در گروه دستور زیر را ارسال کنی:
/acceptlove

اگر نمی‌خواهی این درخواست را قبول کنی:
/declinelove

⏳ این درخواست تا ۳ دقیقه آینده معتبر است.
"""
    bot.send_message(message.chat.id, text)

    # پس از 3 دقیقه حذف درخواست اگر هنوز نپذیرفته شده
    threading.Timer(180, lambda: remove_pending_request(user2.id)).start()

@bot.message_handler(commands=['acceptlove'])
def accept_love(message):
    user2 = message.from_user
    if user2.id not in pending_love_requests:
        return bot.reply_to(message, "❌ درخواستی برای قبول کردن نداری!")

    user1_id, req_time = pending_love_requests[user2.id]
    # ثبت عشق در دیتابیس
    with conn:
        c.execute("INSERT OR REPLACE INTO lovers (user1, user2) VALUES (?, ?)", (user1_id, user2.id))
    del pending_love_requests[user2.id]

    # گرفتن اطلاعات کاربر اول برای پیام
    c.execute("SELECT name, username FROM users WHERE user_id = ?", (user1_id,))
    user1_data = c.fetchone()
    user1_name = user1_data[0] if user1_data else "ناشناس"
    user1_username = user1_data[1] or "ندارد"

    # متن عاشقانه تایید
    text = f"💞 عشق بین [{user1_name}](tg://user?id={user1_id}) و [{user2.first_name}](tg://user?id={user2.id}) ثبت شد! مبارک باشه! 🎉"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['declinelove'])
def decline_love(message):
    user2 = message.from_user
    if user2.id not in pending_love_requests:
        return bot.reply_to(message, "❌ درخواستی برای رد کردن نداری!")
    user1_id, _ = pending_love_requests[user2.id]
    del pending_love_requests[user2.id]

    # گرفتن نام درخواست‌دهنده برای پیام
    c.execute("SELECT name FROM users WHERE user_id = ?", (user1_id,))
    user1_name = c.fetchone()
    user1_name = user1_name[0] if user1_name else "ناشناس"

    text = f"💔 درخواست عشق {user1_name} توسط [{message.from_user.first_name}](tg://user?id={user2.id}) رد شد."
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['divorce'])
def divorce(message):
    user = message.from_user
    c.execute("SELECT user2 FROM lovers WHERE user1 = ?", (user.id,))
    row = c.fetchone()
    if not row:
        return bot.reply_to(message, "❌ عشق ثبت شده‌ای نداری که طلاق بگیری!")
    partner_id = row[0]

    # حذف عشق دوطرفه (اگر وجود داشت)
    with conn:
        c.execute("DELETE FROM lovers WHERE user1 = ? OR user1 = ?", (user.id, partner_id))

    # گرفتن اسم‌ها برای پیام
    c.execute("SELECT name FROM users WHERE user_id = ?", (user.id,))
    name1 = c.fetchone()
    name1 = name1[0] if name1 else "ناشناس"
    c.execute("SELECT name FROM users WHERE user_id = ?", (partner_id,))
    name2 = c.fetchone()
    name2 = name2[0] if name2 else "ناشناس"

    text = f"💔 رابطه عاشقانه بین [{name1}](tg://user?id={user.id}) و [{name2}](tg://user?id={partner_id}) به پایان رسید."
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

bot.infinity_polling()
