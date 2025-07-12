import sqlite3
from telebot import TeleBot
import re

TOKEN = 'توکنتو اینجا بزار'
OWNER_ID = 7341748124
bot = TeleBot(TOKEN)

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

# جدول کاربران
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    country TEXT DEFAULT '🇮🇷 ایران',
    coins INTEGER DEFAULT 180,
    score INTEGER DEFAULT 200,
    golden_badge_manual INTEGER DEFAULT 0,
    birthdate TEXT,
    hashtag TEXT,
    hashtag_reply TEXT,
    message_count INTEGER DEFAULT 0
)''')

# جدول ادمین‌ها
cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)''')

# جدول برای ذخیره وضعیت امتیازدهی (روشن/خاموش)
cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)''')
conn.commit()

def is_owner(uid):
    return uid == OWNER_ID

def is_admin(uid):
    if is_owner(uid):
        return True
    cursor.execute("SELECT 1 FROM admins WHERE user_id=?", (uid,))
    return cursor.fetchone() is not None

def add_admin(user_id):
    cursor.execute("INSERT OR IGNORE INTO admins(user_id) VALUES (?)", (user_id,))
    conn.commit()

def remove_admin(user_id):
    cursor.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    conn.commit()

def remove_all_admins():
    cursor.execute("DELETE FROM admins")
    conn.commit()

def add_user(user_id, first_name, username):
    cursor.execute("INSERT OR IGNORE INTO users(user_id, first_name, username) VALUES (?, ?, ?)", (user_id, first_name, username))
    conn.commit()

def get_user(uid):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    return cursor.fetchone()

def update_score(uid, amt):
    cursor.execute("UPDATE users SET score = score + ? WHERE user_id=?", (amt, uid))
    conn.commit()

def update_coins(uid, amt):
    cursor.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amt, uid))
    conn.commit()

def get_setting(key):
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return None

def set_setting(key, value):
    cursor.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?, ?)", (key, value))
    conn.commit()

def format_profile(user):
    user_id, fname, uname, country, coins, score, _, birth, tag, _, msg_count = user
    uname = f"@{uname}" if uname else "ندارد"
    birth = birth or "ثبت نشده"
    tag = tag or "ثبت نشده"
    badge = "دارد ✅" if score >= 5000 else "ندارد ❌"
    return f"""━━━【 پروفایل شما در گروه 】━━━
•اطلاعات حقیقی•
👤 نام: {fname}
✨ یوزرنیم: {uname}
⚔️ آیدی عددی: {user_id}

🌐 کشور شما: {country}

•• دارایی شما: ••
💰 سکه‌هات: {coins}
💎 امتیازت: {score}
⚜️ نشان تایید طلایی: {badge}

🔮 قدرت‌ها و طلسم‌ها: ثبت نشده
🎂 تاریخ تولدت: {birth}
♨️ هشتگ اختصاصی: {tag}
♥️ شکلک اختصاصی: ثبت نشده
🐣 حیوان مورد علاقه‌ت: ثبت نشده
--------------------------------------
::::: در گروه :::::

▪︎🏆 درجه شما در گروه: ثبت نشده
▪︎💠 مقام شما در گروه: ثبت نشده
"""

# کنترل سیستم امتیازدهی روشن/خاموش
def is_score_system_on():
    val = get_setting("score_system")
    return val == "on"

# روشن کردن سیستم امتیازدهی
@bot.message_handler(commands=['onpm'])
def enable_score_system(m):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, "❌ فقط مدیران و مالک می‌توانند این دستور را اجرا کنند.")
        return
    set_setting("score_system", "on")
    bot.reply_to(m, "✅ سیستم امتیازدهی پیام‌ها روشن شد.")

# خاموش کردن سیستم امتیازدهی
@bot.message_handler(commands=['offpm'])
def disable_score_system(m):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, "❌ فقط مدیران و مالک می‌توانند این دستور را اجرا کنند.")
        return
    set_setting("score_system", "off")
    bot.reply_to(m, "✅ سیستم امتیازدهی پیام‌ها خاموش شد.")

# شمارش پیام‌های کاربران برای امتیازدهی
@bot.message_handler(func=lambda m: True)
def on_message_handler(m):
    uid = m.from_user.id
    add_user(uid, m.from_user.first_name, m.from_user.username)
    if not is_score_system_on():
        return
    cursor.execute("SELECT message_count FROM users WHERE user_id=?", (uid,))
    count = cursor.fetchone()[0]
    count += 1
    cursor.execute("UPDATE users SET message_count=? WHERE user_id=?", (count, uid))
    conn.commit()
    if count % 4 == 0:
        update_score(uid, 1)
        bot.reply_to(m, f"🎉 به ازای ۴ پیام، ۱ امتیاز به حساب شما افزوده شد! امتیاز فعلی: {get_user(uid)[5]}")

# افزایش/کاهش سکه و امتیاز با دستورات ریپلای شده توسط مدیران
@bot.message_handler(func=lambda m: m.reply_to_message and is_admin(m.from_user.id))
def change_coins_or_score(m):
    text = m.text.strip()
    target = m.reply_to_message.from_user
    add_user(target.id, target.first_name, target.username)
    # تغییر سکه با علامت و ایموجی 🪙
    coin_match = re.match(r'^([+-])\s*(\d+)\s*🪙$', text)
    if coin_match:
        sign, amount = coin_match.groups()
        amount = int(amount)
        if sign == '+':
            update_coins(target.id, amount)
            bot.reply_to(m, f"🎁 {amount} سکه به حساب {target.first_name} (@{target.username or 'ندارد'}) افزوده شد!\n🆔 {target.id}")
        else:
            update_coins(target.id, -amount)
            bot.reply_to(m, f"💸 {amount} سکه از حساب {target.first_name} (@{target.username or 'ندارد'}) کم شد!\n🆔 {target.id}")
        return
    # تغییر امتیاز بدون ایموجی، فقط عدد با علامت +/-
    score_match = re.match(r'^([+-])\s*(\d+)$', text)
    if score_match:
        sign, amount = score_match.groups()
        amount = int(amount)
        if sign == '+':
            update_score(target.id, amount)
            bot.reply_to(m, f"⭐ {amount} امتیاز به حساب {target.first_name} (@{target.username or 'ندارد'}) افزوده شد!\n🆔 {target.id}")
        else:
            update_score(target.id, -amount)
            bot.reply_to(m, f"⚡ {amount} امتیاز از حساب {target.first_name} (@{target.username or 'ندارد'}) کم شد!\n🆔 {target.id}")
        return

bot.infinity_polling()
