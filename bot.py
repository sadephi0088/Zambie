import telebot
import sqlite3
import random
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

bot = telebot.TeleBot("7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs")

# آیدی عددی مالک
OWNER_ID = 7341748124

# حالت خوش‌آمدگویی
welcome_enabled = True

# اتصال به دیتابیس
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# ایجاد جدول کاربران
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    nickname TEXT,
    coins INTEGER DEFAULT 250,
    score INTEGER DEFAULT 50,
    gold_medal INTEGER DEFAULT 0,
    powers TEXT DEFAULT '',
    birthday TEXT DEFAULT '',
    hashtag TEXT DEFAULT '',
    motto TEXT DEFAULT '',
    rank TEXT DEFAULT '',
    status TEXT DEFAULT ''
)
''')

# ایجاد جدول بازی‌های فعال
cursor.execute('''
CREATE TABLE IF NOT EXISTS active_games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenger_id INTEGER,
    opponent_id INTEGER DEFAULT 0,
    chat_id INTEGER,
    message_id INTEGER
)
''')
conn.commit()

# ثبت یا بروزرسانی کاربر
def register_user(user):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if cursor.fetchone() is None:
        cursor.execute('''
            INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)
        ''', (user.id, user.first_name or 'بدون نام', user.username or 'ندارد'))
        conn.commit()

# نمایش پروفایل با /mee
@bot.message_handler(commands=['mee'])
def show_profile(message: Message):
    user_id = message.from_user.id
    register_user(message.from_user)
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        bot.reply_to(message, "خطا در دریافت اطلاعات کاربر!")
        return
    
    profile = f"""صفحه شخصی شما در TikTak:

نام: {user[1]}
یوزرنیم: @{user[2]}
لقب: {user[3]}

📦 دارایی‌ها:
سکه‌ها: {user[4]}
امتیاز: {user[5]}
نشان طلایی: {user[6]}

قدرت‌ها: {user[7]}
تولد: {user[8]}
هشتگ: {user[9]}
شعار: {user[10]}

🎖️ درجه: {user[11]}
👑 مقام: {user[12]}
"""
    bot.reply_to(message, profile)

# شروع بازی با /game
@bot.message_handler(commands=['game'])
def start_game(message: Message):
    register_user(message.from_user)
    chat_id = message.chat.id
    challenger = message.from_user

    cursor.execute("SELECT * FROM active_games WHERE chat_id = ?", (chat_id,))
    if cursor.fetchone():
        bot.reply_to(message, "❌ یک بازی در حال اجراست.")
        return

    text = f"""🎲 چالش تاس آغاز شد!

{challenger.first_name} (@{challenger.username or 'ندارد'}) یک بازی تاس راه انداخته!

➕ اگر پایه‌ای، روی دکمه بزن و چالش رو قبول کن.

قوانین:
1️⃣ عدد 1 تا 3 = برد شروع‌کننده (+40)
2️⃣ عدد 4 تا 6 = برد قبول‌کننده (+40)

👇👇👇"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎯 قبول چالش", callback_data="accept_challenge"))
    sent = bot.send_message(chat_id, text, reply_markup=markup)

    cursor.execute("INSERT INTO active_games (challenger_id, chat_id, message_id) VALUES (?, ?, ?)",
                   (challenger.id, chat_id, sent.message_id))
    conn.commit()

# پذیرش چالش
@bot.callback_query_handler(func=lambda c: c.data == "accept_challenge")
def accept_challenge(call: CallbackQuery):
    user = call.from_user
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    cursor.execute("SELECT * FROM active_games WHERE chat_id = ?", (chat_id,))
    game = cursor.fetchone()
    if not game:
        bot.answer_callback_query(call.id, "❌ بازی یافت نشد.")
        return

    challenger_id, opponent_id = game[1], game[2]

    if user.id == challenger_id:
        bot.answer_callback_query(call.id, "❌ نمی‌تونی با خودت بازی کنی!")
        return
    if opponent_id != 0:
        bot.answer_callback_query(call.id, "❌ کسی دیگه بازی رو قبول کرده.")
        return

    cursor.execute("UPDATE active_games SET opponent_id = ? WHERE game_id = ?", (user.id, game[0]))
    conn.commit()

    cursor.execute("SELECT name, username FROM users WHERE user_id = ?", (challenger_id,))
    challenger = cursor.fetchone()
    opponent = (user.first_name or 'بدون نام', user.username or 'ندارد')

    text = f"""🎮 بازی بین:
{challenger[0]} (@{challenger[1]})
و
{opponent[0]} (@{opponent[1]})

🎲 حالا نوبت انداختن تاسه..."""
    bot.edit_message_text(text, chat_id=chat_id, message_id=message_id)

    play_dice_game(chat_id, challenger_id, user.id)

# اجرای بازی تاس
def play_dice_game(chat_id, challenger_id, opponent_id):
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)

    winner_id = challenger_id if d1 <= 3 else opponent_id
    loser_id = opponent_id if winner_id == challenger_id else challenger_id

    # امتیازدهی
    cursor.execute("SELECT score FROM users WHERE user_id = ?", (winner_id,))
    winner_score = cursor.fetchone()[0] + 40

    cursor.execute("SELECT score FROM users WHERE user_id = ?", (loser_id,))
    loser_score = max(0, cursor.fetchone()[0] - 20)

    cursor.execute("UPDATE users SET score = ? WHERE user_id = ?", (winner_score, winner_id))
    cursor.execute("UPDATE users SET score = ? WHERE user_id = ?", (loser_score, loser_id))
    conn.commit()

    cursor.execute("SELECT name FROM users WHERE user_id = ?", (winner_id,))
    winner_name = cursor.fetchone()[0]
    cursor.execute("SELECT name FROM users WHERE user_id = ?", (loser_id,))
    loser_name = cursor.fetchone()[0]

    bot.send_message(chat_id, f"🏆 تبریک {winner_name}! +40 امتیاز برات ثبت شد 🎉")
    bot.send_message(chat_id, f"💔 {loser_name} متأسفم! -20 امتیاز خوردی 😢")

    cursor.execute("DELETE FROM active_games WHERE chat_id = ?", (chat_id,))
    conn.commit()

# روشن کردن خوش‌آمدگویی
@bot.message_handler(commands=['wlc'])
def enable_welcome(message: Message):
    global welcome_enabled
    if message.from_user.id == OWNER_ID:
        welcome_enabled = True
        bot.reply_to(message, "✅ خوش‌آمدگویی فعال شد.")

# خاموش کردن خوش‌آمدگویی
@bot.message_handler(commands=['dwlc'])
def disable_welcome(message: Message):
    global welcome_enabled
    if message.from_user.id == OWNER_ID:
        welcome_enabled = False
        bot.reply_to(message, "❌ خوش‌آمدگویی غیرفعال شد.")

# پیام خوش‌آمدگویی اعضای جدید
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message: Message):
    if not welcome_enabled:
        return
    for user in message.new_chat_members:
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "ندارد ❌"
        text = f"""🎉 خوش‌اومدی {name} عزیز!
🆔 آیدی: {user.id}
🔗 یوزرنیم: {username}
📄 پروفایل اختصاصی‌ت ساخته شد!
👁‍🗨 برای دیدنش بنویس: /mee"""
        bot.send_message(message.chat.id, text, reply_to_message_id=message.message_id)

# اجرای همیشگی ربات
bot.infinity_polling()
