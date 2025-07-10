import telebot
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

bot = telebot.TeleBot("7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs")
OWNER_ID = 7341748124
games = {}

# دکمه‌های بازه ۱۰۰تایی
def send_range_buttons(chat_id, user_id):
    markup = InlineKeyboardMarkup()
    for i in range(1, 801, 100):
        btn_text = f"{i} تا {i+99}"
        data = f"range100:{user_id}:{i}"
        markup.add(InlineKeyboardButton(btn_text, callback_data=data))
    text = "✨ «سلام به قهرمان‌های بازی! 🎲\nربات عددی بین 1 تا 800 انتخاب کرده.\nحدس بزنید عدد طلایی تو کدوم بازه ۱۰۰تایی هست؟ 👑\nدکمه زیر رو فشار بدید و شروع کنیم!»"
    bot.send_message(chat_id, text, reply_markup=markup)

# دکمه‌های بازه ۲۰تایی
def send_subrange_buttons(chat_id, user_id, start):
    markup = InlineKeyboardMarkup()
    for i in range(start, start + 100, 20):
        btn_text = f"{i} تا {i+19}"
        data = f"range20:{user_id}:{i}"
        markup.add(InlineKeyboardButton(btn_text, callback_data=data))
    text = f"🎉 «آفرین! 🥳 تو درست حدس زدی!\nعدد طلایی بین [{start}-{start+99}] هست.\nحالا بیایم بازه رو دقیق‌تر کنیم…\nکدوم بازه ۲۰تایی به نظرت عدد توش هست؟»"
    bot.send_message(chat_id, text, reply_markup=markup)

# دکمه‌های عدد دقیق
def send_final_guess_buttons(chat_id, user_id, start):
    markup = InlineKeyboardMarkup()
    row = []
    for i in range(start, start + 20):
        row.append(InlineKeyboardButton(str(i), callback_data=f"final:{user_id}:{i}"))
        if len(row) == 5:
            markup.add(*row)
            row = []
    if row:
        markup.add(*row)
    text = f"🔥 «عالیه! 🎯\nعدد طلایی بین [{start}-{start+19}] هست.\nبریم مرحله بعد و عدد رو دقیق‌تر حدس بزنیم!»\n\n🌟 «حالا وقت حدس دقیق اعداده!\nاز بین این ۲۰ عدد، عدد طلایی رو پیدا کن! ✨\nبه نوبت حدس بزنید و شانس‌تون رو امتحان کنید!»"
    bot.send_message(chat_id, text, reply_markup=markup)

# شروع بازی با /game
@bot.message_handler(commands=["game"])
def start_game(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in games:
        bot.reply_to(message, "❌ یک بازی در حال اجراست. لطفاً صبر کن تا تموم شه.")
        return

    number = random.randint(1, 800)
    games[chat_id] = {
        "number": number,
        "stage": 1,
        "user_id": user_id
    }

    bot.send_message(chat_id, f"🎲 بازی حدس عدد توسط {message.from_user.first_name} آغاز شد!")
    send_range_buttons(chat_id, user_id)

# هندل دکمه‌ها
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    if chat_id not in games:
        bot.answer_callback_query(call.id, "هیچ بازی فعالی در حال حاضر نیست.")
        return

    game = games[chat_id]
    target = game["number"]
    parts = call.data.split(":")
    if len(parts) != 3:
        return

    step, uid, value = parts[0], int(parts[1]), int(parts[2])

    if user_id != uid:
        bot.answer_callback_query(call.id, "⏳ این بازی مخصوص بازیکن فعلیه عزیزم! صبر کن نوبتت شه 🧡")
        return

    if step == "range100":
        if value <= target <= value + 99:
            bot.answer_callback_query(call.id, "✅ درست گفتی عزیزم! بریم مرحله بعد! 🎉")
            send_subrange_buttons(chat_id, uid, value)
        else:
            bot.answer_callback_query(call.id, "😅 «نه عزیزم، عدد طلایی تو اون بازه نیست، دوباره امتحان کن!\nشجاعتت رو دوست دارم! 💪❤️»")

    elif step == "range20":
        if value <= target <= value + 19:
            bot.answer_callback_query(call.id, "💫 عالیه! فقط یه قدم مونده تا برنده شی 😍")
            send_final_guess_buttons(chat_id, uid, value)
        else:
            bot.answer_callback_query(call.id, "😅 «نه عزیزم، عدد طلایی تو اون بازه نیست، دوباره امتحان کن!\nشجاعتت رو دوست دارم! 💪❤️»")

    elif step == "final":
        if value == target:
            bot.answer_callback_query(call.id, "🏆 وای! درست گفتییییییییی!!! 🎯")
            username = call.from_user.username or "ندارد"
            name = call.from_user.first_name
            result = f"""🏆 «وای! تبریک می‌گم @{username} عزیز! 🎉🎉
تو برنده شدی! جایزه: ۸۰ امتیاز و ۵۰ سکه به حسابت واریز شد! 💰
قهرمان بازی امروز تویی! 👑🌹»"""
            bot.send_message(chat_id, result)
            # 👉 اینجا می‌تونی کد افزایش سکه/امتیاز بزاری
            del games[chat_id]
        else:
            bot.answer_callback_query(call.id, "💔 نه عزیزم... اون عدد نبود! دوباره تلاش کن 😘")

bot.infinity_polling()
