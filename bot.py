import telebot
import random
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# ======== تنظیمات اولیه ========
TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
OWNER_ID = 7341748124

bot = telebot.TeleBot(TOKEN)

# ======== اتصال به دیتابیس ========
conn = sqlite3.connect('game_bot.db', check_same_thread=False)
cursor = conn.cursor()

# ======== ایجاد جدول مدیران ========
cursor.execute('''
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)
''')

# ======== ایجاد جدول کاربران (برای امتیاز و سکه) ========
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0
)
''')

conn.commit()

# ======== ساختار بازی‌ها ========
games = {}  # کلید: chat_id، مقدار: دیکشنری بازی

# ======== توابع کمکی ========

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id):
    cursor.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None or is_owner(user_id)

def add_admin(user_id):
    if not is_admin(user_id):
        cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return True
    return False

def remove_admin(user_id):
    if not is_owner(user_id):
        cursor.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    return False

def clear_admins():
    cursor.execute("DELETE FROM admins WHERE user_id != ?", (OWNER_ID,))
    conn.commit()

def register_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def add_rewards(user_id, coins=0, score=0):
    register_user(user_id)
    cursor.execute("UPDATE users SET coins = coins + ?, score = score + ? WHERE user_id = ?", (coins, score, user_id))
    conn.commit()

def get_username(user):
    return user.username if user.username else str(user.id)

# ======== پیام‌های زیبا ========

def game_start_text(player_list_text):
    return f"""🎲✨ چـــالش بزرگ حدس عدد شروع شد! ✨🎲

🔢 عددی بین ۱ تا ۸۰۰ در ذهن ربات پنهان شده...

می‌تونی پیداش کنی؟ 😃💭

👥 بازیکن‌های که تا الان وارد بازی شدن:

{player_list_text}

🌟 هر چی بازیکن بیشتر، هیجان بیشتر!
برای ورود به بازی روی دکمه زیر بزنی عزیز دلم 😍👇
"""

def game_stopped_text():
    return """🛑 بازی به درخواست یکی از مدیران یا بازیکن آغازکننده متوقف شد.

شاید امروز زمان خوبی برای رقابت نبود...  
ولی همیشه می‌تونی برگردی و دوباره بدرخشی! 🌟💖

🎲 دفعه بعد حتماً می‌بریش، قهرمان! 😘
"""

def winner_text(username):
    return f"""🏆 «وای! تبریک می‌گم @{username} عزیز! 🎉🎉
تو برنده شدی! جایزه: ۸۰ امتیاز و ۵۰ سکه به حسابت واریز شد! 💰
قهرمان بازی امروز تویی! 👑🌹»
"""

def not_correct_guess_text():
    return "😅 «نه عزیزم، عدد طلایی تو اون بازه نیست، دوباره امتحان کن!\nشجاعتت رو دوست دارم! 💪❤️»"

def next_player_turn_text(username):
    return f"⏳ «نوبت به @{username} بعدی رسید!\nمنتظر حدس‌های جذابت هستیم! 🤩»"

# ======== دکمه‌ها ========

def make_join_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ منم بازی می‌کنم!", callback_data="join_game"))
    return markup

def make_start_stop_markup(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎯 شروع بازی", callback_data="start_game"))
    markup.add(InlineKeyboardButton("❌ پایان بازی", callback_data="stop_game"))
    return markup

# ======== فرمان‌ها ========

@bot.message_handler(commands=['setadmin'])
def cmd_setadmin(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ فقط مالک ربات می‌تونه مدیر تعیین کنه عزیزم!")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "🔄 لطفاً این دستور رو ریپلای روی پیام شخص موردنظر بفرست.")
        return
    user = message.reply_to_message.from_user
    if is_admin(user.id):
        bot.reply_to(message, f"👑 @{user.username or user.id} قبلاً مدیر بود.")
        return
    add_admin(user.id)
    bot.reply_to(message, f"✅ @{user.username or user.id} به عنوان مدیر ربات ثبت شد. بهش خوش‌آمد بگو! 🎉💖")

@bot.message_handler(commands=['deladmin'])
def cmd_deladmin(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ فقط مالک ربات می‌تونه مدیر حذف کنه عزیزم!")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "🔄 لطفاً این دستور رو ریپلای روی پیام شخص موردنظر بفرست.")
        return
    user = message.reply_to_message.from_user
    if not is_admin(user.id):
        bot.reply_to(message, f"👑 @{user.username or user.id} مدیر نیست.")
        return
    if user.id == OWNER_ID:
        bot.reply_to(message, "❌ نمی‌تونی مالک رو از مدیر حذف کنی عزیزم!")
        return
    remove_admin(user.id)
    bot.reply_to(message, f"❌ @{user.username or user.id} از لیست مدیران ربات حذف شد.")

@bot.message_handler(commands=['dell'])
def cmd_dell(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ فقط مالک ربات می‌تونه این دستور رو اجرا کنه!")
        return
    clear_admins()
    bot.reply_to(message, "🧹 تمام مدیران (به‌جز مالک) از لیست حذف شدند.")

# ======== بازی ========

@bot.message_handler(commands=['game'])
def cmd_game(message):
    chat_id = message.chat.id
    user = message.from_user

    if chat_id in games:
        bot.reply_to(message, "❌ یک بازی در حال اجراست. لطفاً صبر کن تموم شه.")
        return

    # ساخت بازی جدید
    games[chat_id] = {
        "players": {},
        "owner_id": user.id,
        "number": None,
        "stage": 0,  # 0 = ثبت نام, 1 = بازه ۱۰۰تایی, 2 = بازه ۲۰تایی, 3 = حدس نهایی
        "current_range_start": None,
        "current_subrange_start": None,
        "current_player_ids": [],
        "current_turn_index": 0,
        "winner_id": None
    }

    send_join_message(chat_id)

def send_join_message(chat_id):
    game = games[chat_id]
    player_list_text = format_player_list(game["players"])
    text = game_start_text(player_list_text)
    markup = make_join_markup()
    # اضافه کردن دکمه شروع و پایان فقط برای مالک و مدیرها
    markup_start_stop = make_start_stop_markup(chat_id)
    bot.send_message(chat_id, text, reply_markup=markup)

def format_player_list(players_dict):
    if not players_dict:
        return "❌ هنوز کسی وارد بازی نشده."
    text_lines = []
    for i, (uid, info) in enumerate(players_dict.items(), 1):
        username = info.get("username") or str(uid)
        text_lines.append(f"{i}. {username}")
    return "\n".join(text_lines)

@bot.callback_query_handler(func=lambda call: call.data in ["join_game", "start_game", "stop_game"] or call.data.startswith(("range100:", "range20:", "final:")))
def callback_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data

    if chat_id not in games:
        bot.answer_callback_query(call.id, "❌ بازی فعالی وجود ندارد.")
        return

    game = games[chat_id]

    # دسترسی چک برای start و stop
    if data == "start_game" or data == "stop_game":
        if not is_admin(user_id) and user_id != game["owner_id"]:
            bot.answer_callback_query(call.id, "❌ فقط مالک یا مدیران می‌توانند این کار را انجام دهند.")
            return

    if data == "join_game":
        if user_id in game["players"]:
            bot.answer_callback_query(call.id, "😌 شما قبلاً وارد بازی شده‌ای عزیزم.")
            return
        username = call.from_user.username or str(user_id)
        game["players"][user_id] = {"username": username}
        bot.answer_callback_query(call.id, "✅ تو وارد بازی شدی! منتظر بازیکن‌های دیگر باش 😘")
        edit_join_message(chat_id)
        return

    elif data == "start_game":
        if len(game["players"]) < 2:
            bot.answer_callback_query(call.id, "❌ حداقل ۲ بازیکن نیاز است تا بازی شروع شود.")
            return
        if game["stage"] != 0:
            bot.answer_callback_query(call.id, "❌ بازی قبلاً شروع شده است.")
            return
        # انتخاب عدد طلایی
        game["number"] = random.randint(1, 800)
        game["stage"] = 1
        game["current_range_start"] = 1
        game["current_player_ids"] = list(game["players"].keys())
        game["current_turn_index"] = 0
        send_range100_message(chat_id, game["current_range_start"])
        bot.answer_callback_query(call.id, "🎉 بازی شروع شد! عدد طلایی انتخاب شد. به‌درستی حدس بزنید!")

    elif data == "stop_game":
        bot.answer_callback_query(call.id, "🛑 بازی متوقف شد.")
        bot.send_message(chat_id, game_stopped_text())
        del games[chat_id]

    elif data.startswith("range100:") and game["stage"] == 1:
        # داده: range100:<user_id>:<start>
        _, uid, start_str = data.split(":")
        uid = int(uid)
        start = int(start_str)
        if user_id != uid:
            bot.answer_callback_query(call.id, "⏳ این بازی مخصوص بازیکن فعلی است عزیزم! صبر کن نوبتت شه 🧡")
            return
        if not (start <= game["number"] <= start + 99):
            bot.answer_callback_query(call.id, not_correct_guess_text())
            return
        # درست حدس زده
        bot.answer_callback_query(call.id, "✅ درست گفتی عزیزم! بریم مرحله بعد! 🎉")
        game["stage"] = 2
        game["current_subrange_start"] = start
        send_range20_message(chat_id, start)

    elif data.startswith("range20:") and game["stage"] == 2:
        # داده: range20:<user_id>:<start>
        _, uid, start_str = data.split(":")
        uid = int(uid)
        start = int(start_str)
        if user_id != uid:
            bot.answer_callback_query(call.id, "⏳ این بازی مخصوص بازیکن فعلی است عزیزم! صبر کن نوبتت شه 🧡")
            return
        if not (start <= game["number"] <= start + 19):
            bot.answer_callback_query(call.id, not_correct_guess_text())
            return
        bot.answer_callback_query(call.id, "💫 عالیه! فقط یه قدم مونده تا برنده شی 😍")
        game["stage"] = 3
        send_final_guess_message(chat_id, start)

    elif data.startswith("final:") and game["stage"] == 3:
        # داده: final:<user_id>:<guess>
        _, uid, guess_str = data.split(":")
        uid = int(uid)
        guess = int(guess_str)
        if user_id != uid:
            bot.answer_callback_query(call.id, "⏳ این بازی مخصوص بازیکن فعلی است عزیزم! صبر کن نوبتت شه 🧡")
            return
        if guess == game["number"]:
            bot.answer_callback_query(call.id, "🏆 وای! درست گفتییییییییی!!! 🎯")
            username = call.from_user.username or str(user_id)
            add_rewards(user_id, coins=50, score=80)
            bot.send_message(chat_id, winner_text(username))
            del games[chat_id]
        else:
            bot.answer_callback_query(call.id, "💔 نه عزیزم... اون عدد نبود! دوباره تلاش کن 😘")

# ======== ارسال پیام‌های بازی ========

def edit_join_message(chat_id):
    game = games[chat_id]
    player_list_text = format_player_list(game["players"])
    text = game_start_text(player_list_text)
    markup = make_join_markup()
    # اضافه کردن دکمه شروع و پایان فقط برای مالک و مدیرها
    markup_start_stop = make_start_stop_markup(chat_id)
    # باید پیام قبلی رو ادیت کنیم، ولی چون پیام ارسالی را ذخیره نکردیم، برای ساده‌سازی می‌فرستیم پیام جدید
    bot.send_message(chat_id, text, reply_markup=markup)

def send_range100_message(chat_id, start):
    markup = InlineKeyboardMarkup()
    for i in range(1, 801, 100):
        btn_text = f"{i} تا {i+99}"
        data = f"range100:{games[chat_id]['current_player_ids'][games[chat_id]['current_turn_index']]}:{i}"
        markup.add(InlineKeyboardButton(btn_text, callback_data=data))
    text = f"""✨ «سلام به قهرمان‌های بازی! 🎲
ربات عددی بین 1 تا 800 انتخاب کرده.
حدس بزنید عدد طلایی تو کدوم بازه ۱۰۰تایی هست؟ 👑
دکمه زیر رو فشار بدید و شروع کنیم!»"""
    bot.send_message(chat_id, text, reply_markup=markup)

def send_range20_message(chat_id, start):
    markup = InlineKeyboardMarkup()
    for i in range(start, start + 100, 20):
        btn_text = f"{i} تا {i+19}"
        data = f"range20:{games[chat_id]['current_player_ids'][games[chat_id]['current_turn_index']]}:{i}"
        markup.add(InlineKeyboardButton(btn_text, callback_data=data))
    text = f"""🎉 «آفرین! 🥳 تو درست حدس زدی!
عدد طلایی بین [{start}-{start+99}] هست.
حالا بیایم بازه رو دقیق‌تر کنیم…
کدوم بازه ۲۰تایی به نظرت عدد توش هست؟»"""
    bot.send_message(chat_id, text, reply_markup=markup)

def send_final_guess_message(chat_id, start):
    markup = InlineKeyboardMarkup()
    row = []
    for i in range(start, start + 20):
        data = f"final:{games[chat_id]['current_player_ids'][games[chat_id]['current_turn_index']]}:{i}"
        row.append(InlineKeyboardButton(str(i), callback_data=data))
        if len(row) == 5:
            markup.add(*row)
            row = []
    if row:
        markup.add(*row)
    text = f"""🔥 «عالیه! 🎯
عدد طلایی بین [{start}-{start+19}] هست.
بریم مرحله بعد و عدد رو دقیق‌تر حدس بزنیم!

🌟 «حالا وقت حدس دقیق اعداده!
از بین این ۲۰ عدد، عدد طلایی رو پیدا کن! ✨
به نوبت حدس بزنید و شانس‌تون رو امتحان کنید!»"""
    bot.send_message(chat_id, text, reply_markup=markup)

# ======== اجرای ربات ========
print("ربات بازی حدس عدد با مدیریت مدیران آماده به کار است...")
bot.infinity_polling()
