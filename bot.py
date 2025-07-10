import telebot
import sqlite3
import time
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
    message_id INTEGER
)
''')
conn.commit()

# برای ذخیره وضعیت بازی‌ها (مقدار تاس و پیام‌ها)
active_games_state = {}  # key: chat_id, value: dict with dice values and message_ids

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
منتظر تاس‌ها باشید..."""
    bot.edit_message_text(text, chat_id=chat_id, message_id=message_id)
    
    # ذخیره وضعیت بازی
    active_games_state[chat_id] = {
        'challenger_id': challenger_id,
        'opponent_id': user.id,
        'dice_values': {},
        'dice_message_ids': {}
    }
    
    # فرستادن تاس اول
    dice1 = bot.send_dice(chat_id)
    active_games_state[chat_id]['dice_message_ids']['challenger'] = dice1.message_id

@bot.message_handler(content_types=['dice'])
def handle_dice(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if chat_id not in active_games_state:
        return
    
    game = active_games_state[chat_id]
    challenger_id = game['challenger_id']
    opponent_id = game['opponent_id']
    
    # تشخیص اینکه این تاس برای کدوم بازیکنه
    if user_id == challenger_id and 'challenger' not in game['dice_values']:
        game['dice_values']['challenger'] = message.dice.value
        game['dice_message_ids']['challenger'] = message.message_id
        
        # بعد از تاس اول، تاس دوم رو بنداز
        dice2 = bot.send_dice(chat_id)
        game['dice_message_ids']['opponent'] = dice2.message_id
        
    elif user_id == opponent_id and 'opponent' not in game['dice_values']:
        # ولی بازیکن دوم که تایید کرده ما تاس دوم رو خودمون انداختیم، پس این حالت کم پیش میاد
        # چون ما تاس دوم رو ربات میفرسته
        # اینجا فقط برای اطمینان اگه کاربری خودش تاس زد هست، ذخیره کن
        game['dice_values']['opponent'] = message.dice.value
        game['dice_message_ids']['opponent'] = message.message_id
        
    # اگر هر دو مقدار تاس رسیده بود اعلام نتیجه کن
    if 'challenger' in game['dice_values'] and 'opponent' in game['dice_values']:
        announce_winner(chat_id, game)
        del active_games_state[chat_id]

def announce_winner(chat_id, game):
    challenger_id = game['challenger_id']
    opponent_id = game['opponent_id']
    dice_values = game['dice_values']
    dice_message_ids = game['dice_message_ids']
    
    dice1_value = dice_values['challenger']
    dice2_value = dice_values['opponent']
    
    cursor.execute("SELECT name, username, score FROM users WHERE user_id = ?", (challenger_id,))
    challenger = cursor.fetchone()
    cursor.execute("SELECT name, username, score FROM users WHERE user_id = ?", (opponent_id,))
    opponent = cursor.fetchone()
    
    if 1 <= dice1_value <= 3:
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

    bot.send_message(chat_id, winner_msg, reply_to_message_id=dice_message_ids['challenger'])
    bot.send_message(chat_id, loser_msg, reply_to_message_id=dice_message_ids['opponent'])

    cursor.execute("DELETE FROM active_games WHERE chat_id = ?", (chat_id,))
    conn.commit()

bot.infinity_polling()
