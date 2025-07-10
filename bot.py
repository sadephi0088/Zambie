import telebot
import sqlite3
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

bot = telebot.TeleBot("7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs")

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

cursor.execute('''
CREATE TABLE IF NOT EXISTS active_games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenger_id INTEGER,
    opponent_id INTEGER DEFAULT 0,
    chat_id INTEGER,
    challenger_dice_value INTEGER DEFAULT 0,
    opponent_dice_value INTEGER DEFAULT 0,
    message_id INTEGER
)
''')
conn.commit()

def register_user(user):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if cursor.fetchone() is None:
        cursor.execute('''
            INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)
        ''', (user.id, user.first_name or 'بدون نام', user.username or 'ندارد'))
        conn.commit()

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

@bot.message_handler(commands=['game'])
def start_game(message: Message):
    register_user(message.from_user)
    chat_id = message.chat.id
    challenger = message.from_user
    cursor.execute("SELECT * FROM active_games WHERE chat_id = ?", (chat_id,))
    if cursor.fetchone():
        bot.reply_to(message, "❌ در حال حاضر یک بازی در جریان است، لطفاً صبر کنید تا تمام شود.")
        return
    
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
    
    cursor.execute("INSERT INTO active_games (challenger_id, chat_id, message_id) VALUES (?, ?, ?)",
                   (challenger.id, chat_id, sent.message_id))
    conn.commit()

@bot.callback_query_handler(func=lambda c: c.data == "accept_challenge")
def accept_challenge(call: CallbackQuery):
    user = call.from_user
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    cursor.execute("SELECT * FROM active_games WHERE chat_id = ?", (chat_id,))
    game = cursor.fetchone()
    if not game:
        bot.answer_callback_query(call.id, "❌ بازی فعال پیدا نشد یا تمام شده است.")
        return
    
    challenger_id = game[1]
    opponent_id = game[2]
    
    if user.id == challenger_id:
        bot.answer_callback_query(call.id, "❌ شما نمی‌توانید با خودتان بازی کنید!")
        return
    
    if opponent_id != 0:
        bot.answer_callback_query(call.id, "❌ یک نفر قبلاً چالش را قبول کرده است.")
        return
    
    cursor.execute("UPDATE active_games SET opponent_id = ? WHERE game_id = ?", (user.id, game[0]))
    conn.commit()
    
    cursor.execute("SELECT name, username FROM users WHERE user_id = ?", (challenger_id,))
    challenger = cursor.fetchone()
    cursor.execute("SELECT name, username FROM users WHERE user_id = ?", (user.id,))
    opponent = (user.first_name or 'بدون نام', user.username or 'ندارد')
    
    text = f"""🎲 بازی بین:
👤 {challenger[0]}  @{challenger[1]}
و
👤 {opponent[0]}  @{opponent[1]}

حالا نوبت به تاس انداختن است! 🎲  
منتظر تاس نفر اول باشید..."""
    bot.edit_message_text(text, chat_id=chat_id, message_id=message_id)
    
    # تاس نفر اول رو بنداز
    dice_msg = bot.send_dice(chat_id)
    
    # مقدار تاس نفر اول بعدا در هندلر dice میگیریم
    cursor.execute("UPDATE active_games SET message_id = ? WHERE game_id = ?", (dice_msg.message_id, game[0]))
    conn.commit()
    
    # ارسال پیام و دکمه تاس برای نفر دوم
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎲 تاس بنداز", callback_data="roll_second_dice"))
    bot.send_message(chat_id, f"نفر دوم @{opponent[1]}، دکمه زیر را بزن و تاس خود را بنداز!", reply_markup=markup)

@bot.message_handler(content_types=['dice'])
def handle_dice(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    cursor.execute("SELECT * FROM active_games WHERE chat_id = ?", (chat_id,))
    game = cursor.fetchone()
    if not game:
        return
    
    challenger_id = game[1]
    opponent_id = game[2]
    challenger_dice = game[4]
    opponent_dice = game[5]
    game_id = game[0]
    
    # وقتی تاس نفر اول انداخته نشده و این پیام تاسه، یعنی تاس نفر اول
    if challenger_dice == 0:
        # فقط پیام تاس باید از طرف ربات باشه، چون خود کاربر تاس نمیندازه
        if user_id == bot.get_me().id:
            cursor.execute("UPDATE active_games SET challenger_dice_value = ? WHERE game_id = ?", (message.dice.value, game_id))
            conn.commit()
            bot.send_message(chat_id, "تاس نفر اول انداخته شد! حالا نوبت نفر دوم است.")
            # دکمه برای تاس نفر دوم
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🎲 تاس بنداز", callback_data="roll_second_dice"))
            bot.send_message(chat_id, "نفر دوم، دکمه زیر را بزن و تاس خود را بنداز!", reply_markup=markup)
        return
    
    # وقتی تاس نفر اول اومده و تاس نفر دوم هنوز نیومده
    if opponent_dice == 0 and user_id == bot.get_me().id:
        cursor.execute("UPDATE active_games SET opponent_dice_value = ? WHERE game_id = ?", (message.dice.value, game_id))
        conn.commit()
        # حالا نتیجه رو اعلام کن
        announce_winner(chat_id, game)
        # بازی رو تمیز کن
        cursor.execute("DELETE FROM active_games WHERE game_id = ?", (game_id,))
        conn.commit()
        return

@bot.callback_query_handler(func=lambda c: c.data == "roll_second_dice")
def roll_second_dice(call: CallbackQuery):
    chat_id = call.message.chat.id
    user = call.from_user
    
    cursor.execute("SELECT * FROM active_games WHERE chat_id = ?", (chat_id,))
    game = cursor.fetchone()
    if not game:
        bot.answer_callback_query(call.id, "❌ بازی فعال پیدا نشد یا تمام شده است.")
        return
    
    opponent_id = game[2]
    if user.id != opponent_id:
        bot.answer_callback_query(call.id, "❌ فقط نفر دوم می‌تواند این دکمه را بزند.")
        return
    
    dice_msg = bot.send_dice(chat_id)
    bot.answer_callback_query(call.id, "🎲 تاس انداخته شد!")
    # مقدار تاس نفر دوم در هندلر dice ذخیره می‌شود
    
def announce_winner(chat_id, game):
    challenger_id = game[1]
    opponent_id = game[2]
    challenger_dice = game[4]
    opponent_dice = game[5]
    
    cursor.execute("SELECT name, username, score FROM users WHERE user_id = ?", (challenger_id,))
    challenger = cursor.fetchone()
    cursor.execute("SELECT name, username, score FROM users WHERE user_id = ?", (opponent_id,))
    opponent = cursor.fetchone()
    
    if 1 <= challenger_dice <= 3:
        winner_id = challenger_id
        loser_id = opponent_id
        winner_name = challenger[0]
        winner_username = challenger[1]
        loser_name = opponent[0]
    else:
        winner_id = opponent_id
        loser_id = challenger_id
        winner_name = opponent[0]
        winner_username = opponent[1]
        loser_name = challenger[0]
    
    winner_score = challenger[2] if winner_id == challenger_id else opponent[2]
    loser_score = opponent[2] if loser_id == opponent_id else challenger[2]

    winner_new_score = winner_score + 40
    loser_new_score = max(0, loser_score - 20)

    cursor.execute("UPDATE users SET score = ? WHERE user_id = ?", (winner_new_score, winner_id))
    cursor.execute("UPDATE users SET score = ? WHERE user_id = ?", (loser_new_score, loser_id))
    conn.commit()

    winner_msg = f"""🏆 تبریک {winner_name} عزیز!
🎯 تو این چالش رو بردی و 40 امتیاز شیرین به حسابت اضافه شد 😍
✨ آفرین به شجاعت و شانس بی‌نظیرت! 🔥"""
    loser_msg = f"""💔 اوه نه {loser_name} جان!
🎲 این‌بار شانس باهات یار نبود...
➖ 20 امتیاز ازت کم شد 😢
✨ ولی ناامید نشو، تاس همیشه می‌چرخه!"""

    bot.send_message(chat_id, winner_msg)
    bot.send_message(chat_id, loser_msg)

bot.infinity_polling()
