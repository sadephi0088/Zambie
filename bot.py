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
conn.commit()

# توابع
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def add_user(user_id, first_name, username):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, first_name, username) VALUES (?, ?, ?)",
                   (user_id, first_name, username))
    conn.commit()

def update_score(user_id, amount):
    cursor.execute("UPDATE users SET score = score + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def update_coins(user_id, amount):
    cursor.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def check_golden_badge(user_id):
    cursor.execute("SELECT score, golden_badge_manual FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row:
        score, manual = row
        return manual == 1 or score >= 5000
    return False

def format_profile(user):
    user_id, first_name, username, country, coins, score, _, birthdate, hashtag, _ = user
    username = f"@{username}" if username else "ندارد"
    birthdate = birthdate or "ثبت نشده"
    hashtag = hashtag or "ثبت نشده"
    badge = "دارد ✅" if check_golden_badge(user_id) else "ندارد ❌"

    return f"""━━━【 پروفایل شما در گروه 】━━━
•اطلاعات حقیقی•
👤 نام: {first_name}
✨ یوزرنیم: {username}
⚔️ آیدی عددی: {user_id}

🌐 کشور شما: {country}

•• دارایی شما: ••
💰 سکه‌هات: {coins}
💎 امتیازت: {score}
⚜️ نشان تایید طلایی: {badge}

🔮 قدرت‌ها و طلسم‌ها: ثبت نشده
🎂 تاریخ تولدت: {birthdate}
♨️ هشتگ اختصاصی: {hashtag}
♥️ شکلک اختصاصی: ثبت نشده
🐣 حیوان مورد علاقه‌ت: ثبت نشده
--------------------------------------
::::: در گروه :::::

▪︎🏆 درجه شما در گروه: ثبت نشده
▪︎💠 مقام شما در گروه: ثبت نشده
"""

# دستورات

@bot.message_handler(commands=['start'])
def start(m):
    add_user(m.from_user.id, m.from_user.first_name, m.from_user.username)
    bot.reply_to(m, "✨ ربات با موفقیت فعال شد و پروفایل شما ساخته شد!")

@bot.message_handler(commands=['my'])
def profile(m):
    user = get_user(m.from_user.id)
    if not user:
        add_user(m.from_user.id, m.from_user.first_name, m.from_user.username)
        user = get_user(m.from_user.id)
    bot.reply_to(m, format_profile(user))

@bot.message_handler(commands=['old'])
def set_birthdate(m):
    user_id = m.from_user.id
    add_user(user_id, m.from_user.first_name, m.from_user.username)
    match = re.match(r'^/old\\s+(\\d{3,4}/\\d{1,2}/\\d{1,2})$', m.text.strip())
    if not match:
        bot.reply_to(m, "📅 فرمت درست نیست!\nدرست بنویس مثل: `/old 1378/5/23`", parse_mode="Markdown")
        return
    new_birthdate = match.group(1)
    cursor.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    coins = cursor.fetchone()[0]
    if coins < 25:
        bot.reply_to(m, "❌ موجودی سکه کافی نیست! (نیازمند ۲۵ سکه)")
        return
    cursor.execute("UPDATE users SET birthdate=?, coins=coins-25 WHERE user_id=?", (new_birthdate, user_id))
    conn.commit()
    bot.reply_to(m, f"🎂 تاریخ تولد {new_birthdate} با موفقیت ثبت شد.\n💸 ۲۵ سکه بابت ثبت کسر شد!")

@bot.message_handler(commands=['mytag'])
def set_hashtag(m):
    user_id = m.from_user.id
    add_user(user_id, m.from_user.first_name, m.from_user.username)
    match = re.match(r'^/mytag\\s+(#[^\\s]+)$', m.text.strip())
    if not match:
        bot.reply_to(m, "❗ لطفاً به‌صورت درست وارد کن:\n/mytag #مثال")
        return
    new_tag = match.group(1)
    cursor.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    coins = cursor.fetchone()[0]
    if coins < 80:
        bot.reply_to(m, "💰 سکه کافی برای ثبت هشتگ ندارید! (نیازمند ۸۰ سکه)")
        return
    cursor.execute("UPDATE users SET hashtag=?, hashtag_reply=NULL, coins=coins-80 WHERE user_id=?",
                   (new_tag, user_id))
    conn.commit()
    bot.reply_to(m, f"✅ هشتگ {new_tag} با موفقیت ثبت شد و ۸۰ سکه از حساب شما کسر شد.\n📝 حالا متنی که میخوای برای این هشتگ نمایش داده شه همینجا بنویس!")

@bot.message_handler(func=lambda m: True)
def tag_reply(m):
    user_id = m.from_user.id
    cursor.execute("SELECT hashtag, hashtag_reply FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result and result[0] and result[1] is None:
        cursor.execute("UPDATE users SET hashtag_reply=? WHERE user_id=?", (m.text, user_id))
        conn.commit()
        bot.reply_to(m, "✏️ پاسخ مربوط به هشتگ شما ذخیره شد.")
    else:
        add_user(user_id, m.from_user.first_name, m.from_user.username)
        update_score(user_id, 1)
        update_coins(user_id, 1)

bot.infinity_polling()
