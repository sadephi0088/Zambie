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
    hashtag_reply TEXT
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
    user_id, fname, uname, country, coins, score, _, birth, tag, _ = user
    uname = f"@{uname}" if uname else "ندارد"
    birth = birth or "ثبت نشده"
    tag = tag or "ثبت نشده"
    badge = "دارد ✅" if check_golden_badge(user_id) else "ندارد ❌"
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
def add_or_remove_coins(m):
    match = re.match(r'^([+-])\\s*(\\d+)\\s*🪙$', m.text.strip())
    if not match:
        return
    sign, amount = match.groups()
    amount = int(amount)
    target = m.reply_to_message.from_user
    add_user(target.id, target.first_name, target.username)
    update_coins(target.id, amount if sign == '+' else -amount)
    msg = "🎁" if sign == '+' else "💸"
    bot.reply_to(m, f"{msg} {abs(amount)} سکه {'افزوده شد به' if sign == '+' else 'کم شد از'} {target.first_name} (@{target.username or 'ندارد'})\\n🆔 {target.id}")

bot.infinity_polling()
