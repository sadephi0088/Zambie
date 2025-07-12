import sqlite3
from telebot import TeleBot, types
import re

TOKEN = '7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs'
OWNER_ID = 7341748124
bot = TeleBot(TOKEN)

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    country TEXT DEFAULT '🇮🇷 ایران',
    coins INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0,
    golden_badge_manual INTEGER DEFAULT 0,
    birthdate TEXT,
    hashtag TEXT,
    hashtag_reply TEXT,
    message_count INTEGER DEFAULT 0
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)""")
conn.commit()

def is_owner(uid): 
    return uid == OWNER_ID

def is_admin(uid):
    if is_owner(uid): 
        return True
    cursor.execute("SELECT 1 FROM admins WHERE user_id=?", (uid,))
    return cursor.fetchone() is not None

def add_admin(user_id):
    cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
    conn.commit()

def remove_admin(user_id):
    cursor.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    conn.commit()

def remove_all_admins():
    cursor.execute("DELETE FROM admins")
    conn.commit()

def add_user(user_id, first_name, username):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, first_name, username, coins, score) VALUES (?, ?, ?, 180, 200)",
                   (user_id, first_name, username))
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

def check_golden_badge(uid):
    cursor.execute("SELECT score, golden_badge_manual FROM users WHERE user_id=?", (uid,))
    row = cursor.fetchone()
    return row and (row[0] >= 5000 or row[1] == 1)

def format_profile(user):
    user_id, fname, uname, country, coins, score, _, birth, tag, _, _ = user
    uname = f"@{uname}" if uname else "ندارد"
    birth = birth or "ثبت نشده"
    tag = tag or "ثبت نشده"
    badge = "دارد ✅" if (score >= 5000) else "ندارد ❌"
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

@bot.message_handler(commands=['admin'])
def cmd_add_admin(m):
    if not is_owner(m.from_user.id):
        bot.reply_to(m, "❌ فقط مالک ربات می‌تواند ادمین اضافه کند.")
        return
    if not m.reply_to_message:
        bot.reply_to(m, "⚠️ برای اضافه کردن ادمین، روی پیام فرد ریپلای کنید و /admin را ارسال کنید.")
        return
    target = m.reply_to_message.from_user
    add_admin(target.id)
    bot.reply_to(m, f"✅ {target.first_name} (@{target.username or 'ندارد'}) به مدیران ربات اضافه شد.\n🆔 {target.id}")

@bot.message_handler(commands=['dadmin'])
def cmd_remove_admin(m):
    if not is_owner(m.from_user.id):
        bot.reply_to(m, "❌ فقط مالک ربات می‌تواند ادمین حذف کند.")
        return
    if not m.reply_to_message:
        bot.reply_to(m, "⚠️ برای حذف ادمین، روی پیام فرد ریپلای کنید و /dadmin را ارسال کنید.")
        return
    target = m.reply_to_message.from_user
    remove_admin(target.id)
    bot.reply_to(m, f"✅ {target.first_name} (@{target.username or 'ندارد'}) از مدیران ربات حذف شد.\n🆔 {target.id}")

@bot.message_handler(commands=['ddadmin'])
def cmd_remove_all_admins(m):
    if not is_owner(m.from_user.id):
        bot.reply_to(m, "❌ فقط مالک ربات می‌تواند همه مدیران را حذف کند.")
        return
    remove_all_admins()
    bot.reply_to(m, "✅ همه مدیران ربات حذف شدند.")

@bot.message_handler(commands=['start'])
def start(m):
    user = get_user(m.from_user.id)
    if not user:
        add_user(m.from_user.id, m.from_user.first_name, m.from_user.username)
        bot.reply_to(m, "✨ پروفایل ساخته شد!\n🎁 180 سکه و 200 امتیاز هدیه گرفتی!")
    else:
        bot.reply_to(m, "✨ ربات فعال است و پروفایل شما قبلاً ساخته شده است.")

@bot.message_handler(commands=['my'])
def profile(m):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    add_user(target.id, target.first_name, target.username)
    bot.reply_to(m, format_profile(get_user(target.id)))

@bot.message_handler(commands=['old'])
def set_birthdate(m):
    match = re.match(r'^/old\\s+(\\d{3,4}/\\d{1,2}/\\d{1,2})$', m.text.strip())
    if not match:
        bot.reply_to(m, "📅 فرمت درست نیست! مثل: /old 1380/5/12")
        return
    date = match.group(1)
    uid = m.from_user.id
    add_user(uid, m.from_user.first_name, m.from_user.username)
    coins = get_user(uid)[4]
    if coins < 25:
        bot.reply_to(m, "❌ سکه کافی نیست! (۲۵ تا)")
        return
    cursor.execute("UPDATE users SET birthdate=?, coins=coins-25 WHERE user_id=?", (date, uid))
    conn.commit()
    bot.reply_to(m, f"🎂 تاریخ تولد {date} ثبت شد.\n💸 ۲۵ سکه کم شد!")

@bot.message_handler(commands=['mytag'])
def set_hashtag(m):
    match = re.match(r'^/mytag\\s+(#[^\\s]+)$', m.text.strip())
    if not match:
        bot.reply_to(m, "❗ درست وارد کن: /mytag #مثال")
        return
    tag = match.group(1)
    uid = m.from_user.id
    add_user(uid, m.from_user.first_name, m.from_user.username)
    coins = get_user(uid)[4]
    if coins < 80:
        bot.reply_to(m, "💰 سکه کافی نداری! (۸۰ تا)")
        return
    cursor.execute("UPDATE users SET hashtag=?, hashtag_reply=NULL, coins=coins-80 WHERE user_id=?", (tag, uid))
    conn.commit()
    bot.reply_to(m, f"✅ هشتگ {tag} ثبت شد.\n📝 حالا متنت رو بفرست!")

@bot.message_handler(func=lambda m: True)
def tag_reply(m):
    uid = m.from_user.id
    cursor.execute("SELECT hashtag, hashtag_reply FROM users WHERE user_id=?", (uid,))
    row = cursor.fetchone()
    if row and row[0] and row[1] is None:
        cursor.execute("UPDATE users SET hashtag_reply=? WHERE user_id=?", (m.text, uid))
        conn.commit()
        bot.reply_to(m, "✏️ متن ذخیره شد.")
        return
    add_user(uid, m.from_user.first_name, m.from_user.username)
    update_score(uid, 1)
    update_coins(uid, 1)

@bot.message_handler(func=lambda m: m.reply_to_message and is_admin(m.from_user.id))
def change_coins_or_score(m):
    text = m.text.strip()
    # تغییر سکه با علامت و ایموجی 🪙
    coin_match = re.match(r'^([+-])\\s*(\\d+)\\s*🪙$', text)
    if coin_match:
        sign, amount = coin_match.groups()
        amount = int(amount)
        target = m.reply_to_message.from_user
        add_user(target.id, target.first_name, target.username)
        if sign == '+':
            update_coins(target.id, amount)
            bot.reply_to(m, f"🎁 {amount} سکه به حساب {target.first_name} (@{target.username or 'ندارد'}) افزوده شد!\n🆔 {target.id}")
        else:
            update_coins(target.id, -amount)
            bot.reply_to(m, f"💸 {amount} سکه از حساب {target.first_name} (@{target.username or 'ندارد'}) کم شد!\n🆔 {target.id}")
        return

    # تغییر امتیاز بدون ایموجی، فقط عدد با علامت +/-
    score_match = re.match(r'^([+-])\\s*(\\d+)$', text)
    if score_match:
        sign, amount = score_match.groups()
        amount = int(amount)
        target = m.reply_to_message.from_user
        add_user(target.id, target.first_name, target.username)
        if sign == '+':
            update_score(target.id, amount)
            bot.reply_to(m, f"⭐ {amount} امتیاز به حساب {target.first_name} (@{target.username or 'ندارد'}) افزوده شد!\n🆔 {target.id}")
        else:
            update_score(target.id, -amount)
            bot.reply_to(m, f"⚡ {amount} امتیاز از حساب {target.first_name} (@{target.username or 'ندارد'}) کم شد!\n🆔 {target.id}")
        return

bot.infinity_polling()
