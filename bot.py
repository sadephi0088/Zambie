import sqlite3
from telebot import TeleBot, types

TOKEN = '7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs'
OWNER_ID = 7341748124

bot = TeleBot(TOKEN)

# --- دیتابیس ---
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    country TEXT DEFAULT '🇮🇷 ایران',
    coins INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0,
    golden_badge_manual INTEGER DEFAULT 0
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)''')

conn.commit()

# --- توابع کمکی ---

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id):
    if is_owner(user_id):
        return True
    cursor.execute('SELECT 1 FROM admins WHERE user_id=?', (user_id,))
    return cursor.fetchone() is not None

def add_admin(user_id):
    cursor.execute('INSERT OR IGNORE INTO admins(user_id) VALUES(?)', (user_id,))
    conn.commit()

def remove_admin(user_id):
    cursor.execute('DELETE FROM admins WHERE user_id=?', (user_id,))
    conn.commit()

def reset_admins():
    cursor.execute('DELETE FROM admins')
    conn.commit()

def get_user(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    return cursor.fetchone()

def add_user(user_id, first_name, username):
    cursor.execute('INSERT OR IGNORE INTO users (user_id, first_name, username) VALUES (?, ?, ?)',
                   (user_id, first_name, username))
    conn.commit()

def update_score(user_id, amount):
    cursor.execute('UPDATE users SET score = score + ? WHERE user_id=?', (amount, user_id))
    conn.commit()

def update_coins(user_id, amount):
    cursor.execute('UPDATE users SET coins = coins + ? WHERE user_id=?', (amount, user_id))
    conn.commit()

def set_golden_badge_manual(user_id, value):
    cursor.execute('UPDATE users SET golden_badge_manual = ? WHERE user_id=?', (value, user_id))
    conn.commit()

def check_golden_badge(user_id):
    cursor.execute('SELECT score, golden_badge_manual FROM users WHERE user_id=?', (user_id,))
    row = cursor.fetchone()
    if row:
        score, manual_badge = row
        if manual_badge == 1:
            return True
        if score >= 5000:
            return True
    return False

def format_profile(user):
    user_id, first_name, username, country, coins, score, manual_badge = user
    badge_status = "دارد ✅" if check_golden_badge(user_id) else "ندارد ❌"
    username_display = f"@{username}" if username else "ندارد"
    profile_text = f"""━━━【 پروفایل شما در گروه 】━━━
•اطلاعات حقیقی•
👤 نام: {first_name}
✨ یوزرنیم: {username_display}
⚔️ آیدی عددی: {user_id}

🌐 کشور شما: {country}

•• دارایی شما: ••
💰 سکه‌هات: {coins}
💎 امتیازت: {score}
⚜️ نشان تایید طلایی: {badge_status}

🔮 قدرت‌ها و طلسم‌ها: ثبت نشده
🎂 تاریخ تولدت: ثبت نشده
♨️ هشتگ اختصاصی: ثبت نشده
♥️ شکلک اختصاصی: ثبت نشده
🐣 حیوان مورد علاقه‌ت: ثبت نشده
--------------------------------------
::::: در گروه :::::

▪︎🏆 درجه شما در گروه: ثبت نشده
▪︎💠 مقام شما در گروه: ثبت نشده
"""
    return profile_text

# --- دستورات ---

@bot.message_handler(commands=['start'])
def start_handler(m: types.Message):
    add_user(m.from_user.id, m.from_user.first_name, m.from_user.username)
    bot.reply_to(m, "ربات فعال شد و پروفایل شما ساخته شد!")

@bot.message_handler(commands=['my'])
def my_profile(m: types.Message):
    user = get_user(m.from_user.id)
    if not user:
        add_user(m.from_user.id, m.from_user.first_name, m.from_user.username)
        user = get_user(m.from_user.id)
    text = format_profile(user)
    bot.reply_to(m, text)

# مدیریت مدیران

@bot.message_handler(commands=['admin'])
def add_admin_handler(m: types.Message):
    if not is_owner(m.from_user.id):
        bot.reply_to(m, "شما اجازه این کار را ندارید.")
        return
    if not m.reply_to_message:
        bot.reply_to(m, "لطفا روی پیام فردی ریپلای کنید تا مدیرش کنید.")
        return
    user_id = m.reply_to_message.from_user.id
    if is_admin(user_id):
        bot.reply_to(m, "این فرد قبلاً مدیر است.")
        return
    add_admin(user_id)
    bot.reply_to(m, f"کاربر {user_id} به عنوان مدیر افزوده شد.")

@bot.message_handler(commands=['dadmin'])
def remove_admin_handler(m: types.Message):
    if not is_owner(m.from_user.id):
        bot.reply_to(m, "شما اجازه این کار را ندارید.")
        return
    if not m.reply_to_message:
        bot.reply_to(m, "لطفا روی پیام فردی ریپلای کنید تا مدیرش حذف کنید.")
        return
    user_id = m.reply_to_message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(m, "این فرد مدیر نیست.")
        return
    if user_id == OWNER_ID:
        bot.reply_to(m, "نمی‌توانید مالک را حذف کنید.")
        return
    remove_admin(user_id)
    bot.reply_to(m, f"کاربر {user_id} از مدیران حذف شد.")

@bot.message_handler(commands=['ddadmin'])
def reset_admins_handler(m: types.Message):
    if not is_owner(m.from_user.id):
        bot.reply_to(m, "شما اجازه این کار را ندارید.")
        return
    reset_admins()
    bot.reply_to(m, "تمام مدیران حذف شدند.")

# دستورات نشان طلایی

@bot.message_handler(commands=['ok'])
def ok_handler(m: types.Message):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, "شما اجازه این کار را ندارید.")
        return
    if not m.reply_to_message:
        bot.reply_to(m, "لطفا روی پیام فردی ریپلای کنید.")
        return
    user_id = m.reply_to_message.from_user.id
    set_golden_badge_manual(user_id, 1)
    bot.reply_to(m, f"نشان طلایی برای {user_id} فعال شد.")

@bot.message_handler(commands=['dok'])
def dok_handler(m: types.Message):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, "شما اجازه این کار را ندارید.")
        return
    if not m.reply_to_message:
        bot.reply_to(m, "لطفا روی پیام فردی ریپلای کنید.")
        return
    user_id = m.reply_to_message.from_user.id
    set_golden_badge_manual(user_id, 0)
    bot.reply_to(m, f"نشان طلایی برای {user_id} غیرفعال شد.")

# افزایش امتیاز و سکه (مثال ساده، با هر پیام ۱ امتیاز و ۱ سکه)

@bot.message_handler(func=lambda m: True)
def message_handler(m: types.Message):
    add_user(m.from_user.id, m.from_user.first_name, m.from_user.username)
    update_score(m.from_user.id, 1)
    update_coins(m.from_user.id, 1)

bot.infinity_polling()
