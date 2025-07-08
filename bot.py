import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
bot = telebot.TeleBot(TOKEN)

# دیتابیس و جدول‌ها
def init_db():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        coins INTEGER DEFAULT 300,
        gems INTEGER DEFAULT 15,
        del_power INTEGER DEFAULT 0,
        sokot_power INTEGER DEFAULT 0,
        gardbad_power INTEGER DEFAULT 0,
        shield_active INTEGER DEFAULT 0,
        shield_uses INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()
    if not user:
        cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = cur.fetchone()
    conn.close()
    return user

def update_user_power(user_id, power_field, amount):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {power_field} = {power_field} + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def reduce_coins(user_id, amount):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET coins = coins - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def get_coins(user_id):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    coins = cur.fetchone()[0]
    conn.close()
    return coins

def has_enough_coins(user_id, cost):
    return get_coins(user_id) >= cost

def get_user_powers(user_id):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT del_power, sokot_power, gardbad_power, shield_active, shield_uses FROM users WHERE user_id=?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result

# خوش آمدگویی - پیام ورود با ریپلای به پیام ورود کاربر
welcome_enabled = False

@bot.message_handler(commands=["wlc"])
def wlc_on(message):
    global welcome_enabled
    welcome_enabled = True
    bot.reply_to(message, "🌟 خوش‌آمدگویی روشن شد!")

@bot.message_handler(commands=["dwlc"])
def wlc_off(message):
    global welcome_enabled
    welcome_enabled = False
    bot.reply_to(message, "🌟 خوش‌آمدگویی خاموش شد!")

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    global welcome_enabled
    if not welcome_enabled:
        return
    for member in message.new_chat_members:
        text = f"""╔═━⊱🌟 TikTak • پیام ورود 🌟⊰━═╗  
🎉 به امپراطوری تیک‌تاک خوش‌آمدی {member.full_name} عزیز!💢
🆔 آیدی: {member.id}  
🔗 یوزرنیم: @{member.username if member.username else 'ندارد ❌'}
━━━━━━━━━━━━━━━━━━  

📄 پروفایل اختصاصی‌ت ساخته شد!  
🎭 قدرت‌هات، افتخاراتت، امتیازاتت... همه اینجاست!
👁‍🗨 برای دیدنش، فقط توی گروه بنویس:  
/mee   👈
━━━━━━━━━━━━━━━━━━  
🌟 با عشق، تیم مدیریت TikTak Master"""
        # ارسال پیام خوش‌آمدگویی و ریپلای به پیام ورود تلگرام
        bot.reply_to(message, text)

# پنل /mee

def get_user_panel_text(user):
    del_p, sokot_p, gardbad_p, shield_active, shield_uses = user[5], user[6], user[7], user[8], user[9]

    powers_text = ""
    if del_p > 0:
        powers_text += f"💥 پاک‌کن ({del_p} عدد)\n"
    if sokot_p > 0:
        powers_text += f"🔇 سکوت کاربر ({sokot_p} عدد)\n"
    if gardbad_p > 0:
        powers_text += f"🌪️ گردباد ({gardbad_p} عدد)\n"
    if shield_active == 1:
        powers_text += f"🛡️ سپر امنیتی (فعال، {shield_uses} استفاده باقی‌مانده)\n"

    if powers_text == "":
        powers_text = "❌ هیچ قدرتی خریداری نشده است."

    text = f"""🌟━━━【 پنل شما 】━━━🌟

👤 نام: {user[1] if user[1] else 'نامشخص'}
✨ یوزرنیم شما: @{user[2] if user[2] else 'ندارد ❌'}
🏷️ لقب اختصاصی: ندارد

💼 دارایی شما:
💰 سکه: {user[3]}
💎 الماس: {user[4]}

🔮 قدرت‌ها و طلسم‌ها:
{powers_text}

💼 برای خرید قدرت‌ها به فروشگاه بروید:
/shop"""
    return text

@bot.message_handler(commands=["mee"])
def send_panel(message):
    user = get_user(message.from_user.id)
    text = get_user_panel_text(user)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛒 فروشگاه قدرت‌ها", callback_data="buy_powers"),
        InlineKeyboardButton("📘 راهنمای استفاده", callback_data="usage_guide")
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

# فروشگاه قدرت‌ها

def powers_shop_text():
    return """🎉 به فروشگاه رسمی امپراطوری TikTak خوش اومدی!

اینجا سرزمین قدرت و افتخاره...  
جایی که می‌تونی فرم (قالب استعلام پروفایلت) رو ارتقا بدی،  
قدرت‌های خاص بخری، و تجهیزات منحصر‌به‌فرد مثل:  
📛 لقب اختصاصی  
🎂 تاریخ تولد  
♨️ هشتگ شخصی  
⚔️ طلسم‌های ممنوعه و خیلی بیشتر..."""

def powers_shop_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("💥 پاک‌کن 25 سکه", callback_data="buy_del"),
        InlineKeyboardButton("🔇 سکوت کاربر 45 سکه", callback_data="buy_sokot"),
        InlineKeyboardButton("🌪️ گردباد 90 سکه", callback_data="buy_gardbad"),
        InlineKeyboardButton("🛡️ سپر امنیتی 120 سکه", callback_data="buy_shield"),
    )
    kb.add(InlineKeyboardButton("↩️ بازگشت", callback_data="back_to_shop"))
    return kb

@bot.callback_query_handler(func=lambda call: call.data == "buy_powers")
def show_power_shop(call):
    get_user(call.from_user.id)
    bot.edit_message_text(
        powers_shop_text(),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=powers_shop_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_shop")
def back_to_shop(call):
    bot.edit_message_text(
        "🎉 به فروشگاه رسمی امپراطوری TikTak خوش اومدی!\n\nاینجا سرزمین قدرت و افتخار است...\nفرم و قدرت‌ها را انتخاب و ارتقا بده!",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("🛒 خرید قدرت‌ها", callback_data="buy_powers"),
            InlineKeyboardButton("🎯 تجهیزات شخصی", callback_data="personal_items"),
            InlineKeyboardButton("💟 خرید فرم [سطح بالاتر]", callback_data="buy_form"),
            InlineKeyboardButton("↩️ بازگشت", callback_data="back_main")
        )
    )

# خرید قدرت‌ها

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_power_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    if call.data == "buy_del":
        cost = 25
        power_field = "del_power"
    elif call.data == "buy_sokot":
        cost = 45
        power_field = "sokot_power"
    elif call.data == "buy_gardbad":
        cost = 90
        power_field = "gardbad_power"
    elif call.data == "buy_shield":
        cost = 120
        power_field = "shield_active"
    else:
        bot.answer_callback_query(call.id, "❌ گزینه نامعتبر!")
        return

    if power_field == "shield_active":
        if user[8] >= 1:  # shield_active > 0
            bot.answer_callback_query(call.id, "🛡️ شما هم‌اکنون سپر فعال دارید!")
            return

    if has_enough_coins(user_id, cost):
        reduce_coins(user_id, cost)
        if power_field == "shield_active":
            conn = sqlite3.connect("data.db")
            cur = conn.cursor()
            cur.execute("UPDATE users SET shield_active = 1, shield_uses = 2 WHERE user_id=?", (user_id,))
            conn.commit()
            conn.close()
            bot.answer_callback_query(call.id, "✅ سپر امنیتی فعال شد!")
        else:
            update_user_power(user_id, power_field, 1)
            bot.answer_callback_query(call.id, f"✅ قدرت با موفقیت خریداری شد!")
    else:
        bot.answer_callback_query(call.id, "❌ سکه کافی نداری!")

# استفاده از قدرت پاک‌کن

@bot.message_handler(commands=["del"])
def use_del_power(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ لطفا این دستور را ریپلای به پیام فرد مورد نظر ارسال کنید.")
        return
    user_id = message.from_user.id
    user = get_user(user_id)
    if user[5] <= 0:
        bot.reply_to(message, "❌ شما قدرت پاک‌کن ندارید یا تمام شده است.")
        return
    target_msg_id = message.reply_to_message.message_id
    target_chat_id = message.chat.id
    try:
        bot.delete_message(target_chat_id, target_msg_id)
        update_user_power(user_id, "del_power", -1)
        bot.reply_to(message, f"✅ پیام با موفقیت پاک شد.\nتعداد باقی‌مانده: {user[5]-1}")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در حذف پیام: {str(e)}")

# استفاده از قدرت سکوت

@bot.message_handler(commands=["sokot"])
def use_sokot_power(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ لطفا این دستور را ریپلای به پیام فرد مورد نظر ارسال کنید.")
        return
    user_id = message.from_user.id
    user = get_user(user_id)
    if user[6] <= 0:
        bot.reply_to(message, "❌ شما قدرت سکوت ندارید یا تمام شده است.")
        return

    target_user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    target = get_user(target_user_id)

    # چک سپر امنیتی هدف
    if target[8] == 1 and target[9] > 0:
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        cur.execute("UPDATE users SET shield_uses = shield_uses - 1 WHERE user_id=?", (target_user_id,))
        cur.execute("SELECT shield_uses FROM users WHERE user_id=?", (target_user_id,))
        uses_left = cur.fetchone()[0]
        if uses_left <= 0:
            cur.execute("UPDATE users SET shield_active = 0 WHERE user_id=?", (target_user_id,))
        conn.commit()
        conn.close()
        bot.reply_to(message, "🛡️ سپر امنیتی فعال شد! سکوت شما دفع شد و قدرت مصرف نشد.")
        return

    # اگر کاربر هدف قدرت گردباد داره
    if target[7] > 0:
        bot.reply_to(message, """
🌪️💥 قدرت گردباد فعال شد! 💥🌪️
تو خواستی سکوتش کنی... اما غافل از اینکه خودش ارباب بادهاست!

🤣 حالا این تویی که برای ۴۵ ثانیه توی طوفان سکوت فرو میری!

🌀 بادها به فرمان او وزیدند... و تو ساکت شدی 😌
""")
        update_user_power(target_user_id, "gardbad_power", -1)
        bot.restrict_chat_member(chat_id, user_id, until_date=int(message.date)+45, can_send_messages=False)
        return

    try:
        bot.restrict_chat_member(chat_id, target_user_id, until_date=int(message.date)+45, can_send_messages=False)
        update_user_power(user_id, "sokot_power", -1)
        bot.reply_to(message, f"✅ فرد مورد نظر سکوت شد.\nتعداد باقی‌مانده: {user[6]-1}")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در سکوت کاربر: {str(e)}")

# استارت اولیه و مقداردهی دیتابیس
init_db()

print("Bot started...")

bot.infinity_polling()
