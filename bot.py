import sqlite3
import os
import re
from flask import Flask, request
from telebot import TeleBot, types

TOKEN = 'توکن رباتت رو اینجا بزار'
OWNER_ID = 7341748124  # آیدی عددی خودت رو اینجا بذار

bot = TeleBot(TOKEN)
app = Flask(__name__)

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

# جداول اصلی
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

cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)''')
conn.commit()

# فانکشن‌های کمکی
def is_owner(uid):
    return uid == OWNER_ID

def is_admin(uid):
    if is_owner(uid): return True
    cursor.execute("SELECT 1 FROM admins WHERE user_id=?", (uid,))
    return cursor.fetchone() is not None

def add_user(uid, name, username):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, first_name, username) VALUES (?, ?, ?)", (uid, name, username))
    conn.commit()

def update_score(uid, amt):
    cursor.execute("UPDATE users SET score = score + ? WHERE user_id=?", (amt, uid))
    conn.commit()

def update_coins(uid, amt):
    cursor.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amt, uid))
    conn.commit()

def get_setting(key):
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    r = cursor.fetchone()
    return r[0] if r else None

def set_setting(key, value):
    cursor.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?, ?)", (key, value))
    conn.commit()

def is_score_system_on():
    return get_setting("score_system") == "on"

def get_user(uid):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    return cursor.fetchone()

def format_profile(user):
    uid, fname, uname, country, coins, score, _, birth, tag, _, _ = user
    uname = f"@{uname}" if uname else "ندارد"
    birth = birth or "ثبت نشده"
    tag = tag or "ثبت نشده"
    badge = "دارد ✅" if score >= 5000 else "ندارد ❌"
    return f"""━━━【 پروفایل شما در گروه 】━━━
•اطلاعات حقیقی•
👤 نام: {fname}
✨ یوزرنیم: {uname}
⚔️ آیدی عددی: {uid}

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

# مدیریت ادمین
@bot.message_handler(commands=['admin'])
def add_admin_cmd(m):
    if not is_owner(m.from_user.id) or not m.reply_to_message: return
    uid = m.reply_to_message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO admins(user_id) VALUES (?)", (uid,))
    conn.commit()
    bot.reply_to(m, f"✅ ادمین اضافه شد: {uid}")

@bot.message_handler(commands=['dadmin'])
def del_admin_cmd(m):
    if not is_owner(m.from_user.id) or not m.reply_to_message: return
    uid = m.reply_to_message.from_user.id
    cursor.execute("DELETE FROM admins WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m, f"❌ ادمین حذف شد: {uid}")

@bot.message_handler(commands=['ddadmin'])
def reset_admins(m):
    if not is_owner(m.from_user.id): return
    cursor.execute("DELETE FROM admins")
    conn.commit()
    bot.reply_to(m, "🧹 همه ادمین‌ها پاک شدند.")

# نمایش پروفایل
@bot.message_handler(commands=['my'])
def my_profile(m):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    add_user(target.id, target.first_name, target.username)
    bot.reply_to(m, format_profile(get_user(target.id)))

# روشن/خاموش کردن امتیاز پیام
@bot.message_handler(commands=['onpm'])
def turn_on_pm(m):
    if not is_admin(m.from_user.id): return
    set_setting("score_system", "on")
    bot.reply_to(m, "🌟 امتیازدهی روشن شد.")

@bot.message_handler(commands=['offpm'])
def turn_off_pm(m):
    if not is_admin(m.from_user.id): return
    set_setting("score_system", "off")
    bot.reply_to(m, "🌙 امتیازدهی خاموش شد.")

# تغییر سکه و امتیاز با ریپلای
@bot.message_handler(func=lambda m: m.reply_to_message and is_admin(m.from_user.id))
def change_coins_score(m):
    text = m.text.strip()
    target = m.reply_to_message.from_user
    add_user(target.id, target.first_name, target.username)

    # سکه
    c = re.match(r'^([+-])\s*(\d+)\s*🪙$', text)
    if c:
        op, val = c.groups()
        val = int(val)
        update_coins(target.id, val if op == '+' else -val)
        bot.reply_to(m, f"{'🎁 واریز' if op == '+' else '💸 برداشت'} {val} 🪙 برای {target.first_name} | ID: {target.id}")
        return

    # امتیاز
    s = re.match(r'^([+-])\s*(\d+)$', text)
    if s:
        op, val = s.groups()
        val = int(val)
        update_score(target.id, val if op == '+' else -val)
        bot.reply_to(m, f"{'✨ اضافه' if op == '+' else '⚡ کاهش'} {val} امتیاز برای {target.first_name} | ID: {target.id}")
        return

# شمارش پیام برای امتیاز
@bot.message_handler(func=lambda m: True)
def count_messages(m):
    uid = m.from_user.id
    add_user(uid, m.from_user.first_name, m.from_user.username)
    if not is_score_system_on(): return
    cursor.execute("SELECT message_count FROM users WHERE user_id=?", (uid,))
    msg = cursor.fetchone()[0] + 1
    cursor.execute("UPDATE users SET message_count=? WHERE user_id=?", (msg, uid))
    conn.commit()
    if msg % 4 == 0:
        update_score(uid, 1)
        bot.send_message(m.chat.id, f"🌟 {m.from_user.first_name} عزیز! بابت ۴ پیام، ۱ امتیاز گرفتی!")

# ---- Webhook setup برای Render ----
WEBHOOK_URL = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return "ربات با عشق فعاله عزیزم 😘", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
