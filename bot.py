import telebot
import sqlite3
import random
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

bot = telebot.TeleBot("7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs")

# دیتابیس و جدول کاربران
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
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
conn.commit()

# جدول بازی‌های فعال (user_id شروع کننده)
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

# دستور /mee برای نمایش پروفایل (کد ساده شده از قبل)
@bot.message_handler(commands=['mee'])
def show_profile(message: Message):
    user_id = message.from_user.id
    register_user(message.from_user)
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        bot.reply_to(message, "خطا در دریافت اطلاعات کاربر!")
        return
    
    profile_text = f"""【 صفحه شخصی شما در TikTak 】

👤 نام: {user[1]}
✨ یوزرنیم: @{user[2]}
🏷️ لقب اختصاصی: {user[3]}

━━ 【 دارایی شما: 】 ━━
  💰سکه‌ها: {user[4]}
       🌀امتیاز: {user[5]}
       ⚜️ نشان طلایی: {user[6]}

-🔮 قدرت‌ها و طلسم‌ها: {user[7]}
-🎂 تاریخ تولد: {user[8]}
-♨️ هشتگ اختصاصی: {user[9]}
-⚔️ شعار شما: {user[10]}

🌟━━━ 【 در گروه 】 ━━━🌟

🏆درجه شما: {user[11]}
💠 مقام شما: {user[12]}
"""
    bot.reply_to(message, profile_text)

# دستور /game برای شروع بازی تاس
@bot.message_handler(commands=['game'])
def start_game(message: Message):
    register_user(message.from_user)
    chat_id = message.chat.id
    challenger = message.from_user
    # چک کنیم بازی فعالی توی این چت نیست
    cursor.execute("SELECT * FROM active_games WHERE chat_id = ?", (chat_id,))
    if cursor.fetchone():
        bot.reply_to(message, "❌ در حال حاضر یک بازی در جریان است، لطفاً صبر کنید تا تمام شود.")
        return
    
    # ایجاد پیام شروع بازی
    text = f"""🎲🔥 چالش تاس شروع شد! 🔥🎲

کاربر 👤 {challenger.first_name or 'بدون نام'}  
با یوزرنیم ✨ @{challenger.username or 'ندارد'}  
یک بازی تاس راه انداخته و آماده‌ی چالش است! 💥

💢 آیا پایه‌ای برای این رقابت؟  
🍀 شاید سرنوشت با تو یار باشد...

⚠️ قوانین بازی:
1️⃣ اگر عدد تاس بین 1 تا 3 بیاید ➜ فرستنده چالش برنده می‌شود +40 امتیاز  
2️⃣ اگر عدد بین 4 تا 6 بیاید ➜ قبول‌کننده چالش برنده می‌شود +40 امتیاز

🕹️ دکمه زیر را بزن و چالش را قبول کن!

👇👇👇"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎯 شرکت در چالش!", callback_data="accept_challenge"))
    sent = bot.send_message(chat_id, text, reply_markup=markup)
    
    # ثبت بازی فعال
    cursor.execute("INSERT INTO active_games (challenger_id, chat_id, message_id) VALUES (?, ?, ?)",
                   (challenger.id, chat_id, sent.message_id))
    conn.commit()

# هندلر قبول چالش
@bot.callback_query_handler(func=lambda c: c.data == "accept_challenge")
def accept_challenge(call: CallbackQuery):
    user = call.from_user
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # بررسی وجود بازی فعال
    cursor.execute("SELECT * FROM active_games WHERE chat_id = ?", (chat_id,))
    game = cursor.fetchone()
    if not game:
        bot.answer_callback_query(call.id, "❌ بازی فعال پیدا نشد یا تمام شده است.")
        return
    
    challenger_id = game[1]
    opponent_id = game[2]
    
    # بررسی اینکه بازیکن خودش چالش رو شروع نکرده باشه
    if user.id == challenger_id:
        bot.answer_callback_query(call.id, "❌ شما نمی‌توانید با خودتان بازی کنید!")
        return
    
    # اگر نفر دوم قبلاً انتخاب شده بود
    if opponent_id != 0:
        bot.answer_callback_query(call.id, "❌ یک نفر قبلاً چالش را قبول کرده است.")
        return
    
    # ثبت نفر دوم
    cursor.execute("UPDATE active_games SET opponent_id = ? WHERE game_id = ?", (user.id, game[0]))
    conn.commit()
    
    # ارسال پیام اعلام شروع بازی و رول تاس
    cursor.execute("SELECT name, username FROM users WHERE user_id = ?", (challenger_id,))
    challenger = cursor.fetchone()
    cursor.execute("SELECT name, username FROM users WHERE user_id = ?", (user.id,))
    opponent = (user.first_name or 'بدون نام', user.username or 'ندارد')
    
    text = f"""🎲 بازی بین:
👤 {challenger[0]}  @{challenger[1]}
و
👤 {opponent[0]}  @{opponent[1]}

حالا نوبت به تاس انداختن است! 🎲  
برای هر دو نفر عدد تاس ریخته می‌شود..."""
    bot.edit_message_text(text, chat_id=chat_id, message_id=message_id)
    
    # شروع بازی و رول تاس
    play_dice_game(chat_id, challenger_id, user.id)

def play_dice_game(chat_id, challenger_id, opponent_id):
    # رول تاس برای هر دو نفر
    dice_challenger = random.randint(1,6)
    dice_opponent = random.randint(1,6)

    # تعیین برنده بر اساس قانون
    # اگر عدد تاس چالشر بین 1 تا 3 بود برنده challenger است
    # در غیر اینصورت opponent برنده است
    if 1 <= dice_challenger <= 3:
        winner_id = challenger_id
        loser_id = opponent_id
    else:
        winner_id = opponent_id
        loser_id = challenger_id

    # آپدیت امتیازها در دیتابیس
    cursor.execute("SELECT score FROM users WHERE user_id = ?", (winner_id,))
    winner_score = cursor.fetchone()[0]
    cursor.execute("SELECT score FROM users WHERE user_id = ?", (loser_id,))
    loser_score = cursor.fetchone()[0]

    winner_new_score = winner_score + 40
    loser_new_score = max(0, loser_score - 20)  # نذار منفی بشه

    cursor.execute("UPDATE users SET score = ? WHERE user_id = ?", (winner_new_score, winner_id))
    cursor.execute("UPDATE users SET score = ? WHERE user_id = ?", (loser_new_score, loser_id))
    conn.commit()

    # گرفتن نام و یوزرنیم برای پیام‌ها
    cursor.execute("SELECT name, username FROM users WHERE user_id = ?", (winner_id,))
    winner = cursor.fetchone()
    cursor.execute("SELECT name, username FROM users WHERE user_id = ?", (loser_id,))
    loser = cursor.fetchone()

    # ارسال پیام برنده
    winner_msg = f"""🏆 تبریک {winner[0]} عزیز!
🎯 تو این چالش رو بردی و 40 امتیاز شیرین به حسابت اضافه شد 😍
✨ آفرین به شجاعت و شانس بی‌نظیرت! 🔥"""

    # ارسال پیام بازنده
    loser_msg = f"""💔 اوه نه {loser[0]} جان!
🎲 این‌بار شانس باهات یار نبود...
➖ 20 امتیاز ازت کم شد 😢
✨ ولی ناامید نشو، تاس همیشه می‌چرخه!"""

    bot.send_message(chat_id, winner_msg)
    bot.send_message(chat_id, loser_msg)

    # حذف بازی فعال
    cursor.execute("DELETE FROM active_games WHERE chat_id = ?", (chat_id,))
    conn.commit()

bot.infinity_polling()
