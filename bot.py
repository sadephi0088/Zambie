import telebot
import sqlite3
import re
import time

TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
OWNER_ID = 7341748124

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    coin INTEGER DEFAULT 180,
    score INTEGER DEFAULT 250,
    gold_tick INTEGER DEFAULT 0,
    role TEXT DEFAULT 'ممبر عادی 🧍',
    birthdate TEXT DEFAULT '',
    love INTEGER DEFAULT 0,
    child TEXT DEFAULT '',
    pet TEXT DEFAULT '',
    emoji TEXT DEFAULT ''
)
''')
conn.commit()

def add_user(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username or ""
    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)", (user_id, name, username))
        conn.commit()

def update_field(user_id, field, value):
    c.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()

def get_user_data(user_id):
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return c.fetchone()

def get_rank(score):
    if score < 500: return "تازه‌کار 👶"
    elif score < 1000: return "حرفه‌ای 🔥"
    elif score < 2000: return "استاد 🌟"
    elif score < 4000: return "قهرمان 🏆"
    elif score < 7000: return "افسانه‌ای 🐉"
    elif score < 10000: return "بی‌نظیر 💎"
    else: return "اسطوره 🚀"

@bot.message_handler(commands=['my'])
def show_profile(message):
    add_user(message)
    user_id = message.from_user.id
    data = get_user_data(user_id)
    if data:
        tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"
        rank = get_rank(data[4])
        role = data[6] if data[6] else "ممبر عادی 🧍"
        birthdate = data[7]
        lover_id = data[8]
        if lover_id:
            c.execute("SELECT name FROM users WHERE user_id = ?", (lover_id,))
            lover_data = c.fetchone()
            lover_name = lover_data[0] if lover_data else ""
        else:
            lover_name = ""
        
        child = data[9]
        pet = data[10]
        emoji = data[11]

        text = f'''
━━━【 پروفایل دوست‌داشتنی شما 】━━━

👤 نام: {data[1]}
✨ یوزرنیم: @{data[2]}
⚔️ آیدی عددی: {data[0]}
🌐 کشور شما: 🇮🇷 ایران

💰 سکه‌ها: {data[3]}
💎 امتیازها: {data[4]}
⚜️ تیک طلایی: {tick}

❤️ عشق تو: {lover_name}
👶 فرزند عزیزت: {child}
🐾 حیوان خانگی: {pet}
🌙 شکلک اختصاصی: {emoji}
🎂 تاریخ تولد: {birthdate}

▪︎🏆 درجه شما: {rank}
▪︎💠 مقام شما: {role}
'''
        bot.reply_to(message, text)

@bot.message_handler(commands=['old'])
def set_birthdate(message):
    add_user(message)
    user_id = message.from_user.id
    match = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', message.text.strip())
    if not match:
        return bot.reply_to(message, "❌ فرمت اشتباه! درستش اینه:\n/old 1379/1/11")
    birth = match.group(1)

    c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if not data or data[0] < 40:
        return bot.reply_to(message, "❌ برای ثبت تولد باید ۴۰ سکه داشته باشی!")

    update_field(user_id, "birthdate", birth)
    c.execute("UPDATE users SET coin = coin - 40 WHERE user_id = ?", (user_id,))
    conn.commit()
    bot.reply_to(message, "🎂 تاریخ تولد شما ثبت شد و ۴۰ سکه از حسابت کسر شد.")

@bot.message_handler(commands=['love'])
def set_love(message):
    add_user(message)
    if not message.reply_to_message:
        return bot.reply_to(message, "💌 برای ثبت عشق باید روی پیام شخص ریپلای کنی.")
    lover_id = message.from_user.id
    target_id = message.reply_to_message.from_user.id
    if lover_id == target_id:
        return bot.reply_to(message, "😅 نمی‌تونی عاشق خودت باشی عزیزم.")
    c.execute("SELECT coin FROM users WHERE user_id = ?", (lover_id,))
    data = c.fetchone()
    if not data or data[0] < 30:
        return bot.reply_to(message, "❌ برای ثبت عشق باید ۳۰ سکه داشته باشی.")
    update_field(lover_id, "love", target_id)
    c.execute("UPDATE users SET coin = coin - 30 WHERE user_id = ?", (lover_id,))
    conn.commit()
    bot.reply_to(message, "💘 عشق شما ثبت شد. حالا منتظر جواب معشوق باش.")

@bot.message_handler(commands=['child'])
def set_child(message):
    add_user(message)
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(message, "❌ لطفا اسم فرزندتو بنویس مثل:\n/child علی")
    child_name = parts[1]

    c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if not data or data[0] < 50:
        return bot.reply_to(message, "❌ برای ثبت فرزند باید ۵۰ سکه داشته باشی.")
    update_field(user_id, "child", child_name)
    c.execute("UPDATE users SET coin = coin - 50 WHERE user_id = ?", (user_id,))
    conn.commit()
    bot.reply_to(message, f"👶 اسم فرزندت ثبت شد و ۵۰ سکه از حسابت کسر شد.")

@bot.message_handler(commands=['pet'])
def set_pet(message):
    add_user(message)
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(message, "❌ لطفا اسم حیوان خانگی‌تو بنویس مثل:\n/pet سگ")
    pet_name = parts[1]

    c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if not data or data[0] < 50:
        return bot.reply_to(message, "❌ برای ثبت حیوان خانگی باید ۵۰ سکه داشته باشی.")
    update_field(user_id, "pet", pet_name)
    c.execute("UPDATE users SET coin = coin - 50 WHERE user_id = ?", (user_id,))
    conn.commit()
    bot.reply_to(message, f"🐾 حیوان خانگی تو ثبت شد و ۵۰ سکه از حسابت کم شد.")

@bot.message_handler(commands=['emoji'])
def set_emoji(message):
    add_user(message)
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(message, "❌ لطفا شکلک اختصاصیت رو ارسال کن مثل:\n/emoji 😍")
    emoji = parts[1]

    c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if not data or data[0] < 30:
        return bot.reply_to(message, "❌ برای ثبت شکلک باید ۳۰ سکه داشته باشی.")
    update_field(user_id, "emoji", emoji)
    c.execute("UPDATE users SET coin = coin - 30 WHERE user_id = ?", (user_id,))
    conn.commit()
    bot.reply_to(message, f"🌙 شکلک اختصاصی شما ثبت شد و ۳۰ سکه از حسابت کم شد.")

# بقیه دستورات مثل /tik و /dtik و ... رو هم میتونی به همین شکل اضافه کنی

bot.infinity_polling()
