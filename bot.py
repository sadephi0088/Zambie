import telebot
from telebot import types
import re
from collections import defaultdict

TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
bot = telebot.TeleBot(TOKEN)

users = defaultdict(lambda: {
    "coins": 180,
    "points": 200,
    "birthday": "",
    "hashtag": "",
    "emoji": "",
    "pets": []
})

admins = set()
owner_id = 123456789  # آی‌دی عددی خودت رو اینجا بذار

pet_store = {
    "🐺": ("گرگ", 150),
    "🦁": ("شیر", 350),
    "🐉": ("اژدها", 400),
    "🐣": ("جوجه", 45),
    "🐰": ("خرگوش", 35),
    "🦊": ("روباه", 45),
    "🐱": ("گربه", 30),
    "🐶": ("سگ", 45),
    "🐪": ("شتر", 60),
    "🦌": ("گوزن", 30),
    "🦈": ("کوسه", 55),
    "🐆": ("پلنگ", 90)
}

def is_admin(user_id):
    return user_id == owner_id or user_id in admins

# --- دستور /my برای نمایش پروفایل ---
@bot.message_handler(commands=["my"])
def my_profile(message):
    user_id = message.from_user.id
    user = users[user_id]

    name = message.from_user.first_name or "ندارد"
    username = f"@{message.from_user.username}" if message.from_user.username else "ندارد"
    user_id_str = str(user_id)
    country = "🇮🇷 ایران"

    pets_text = " - ".join([f"{e} {n}" for e, n in user["pets"]]) if user["pets"] else "ندارد"

    golden_mark = "✅" if user.get("golden_mark", False) else "❌"

    text = f"""
━━━【 پروفایل شما در گروه 】━━━
•اطلاعات حقیقی•
👤 نام: {name}
✨ یوزرنیم: {username}
⚔️ ایدی عددی: {user_id_str}

🌐 کشور شما: {country}

•• دارایی شما: ••
💰 سکه‌هات: {user['coins']}
💎 امتیازت: {user['points']}
⚜️ نشان تایید طلایی: {golden_mark}

🔮 قدرت‌ها و طلسم‌ها:
🎂 تاریخ تولدت: {user['birthday'] if user['birthday'] else 'ثبت نشده'}
♨️ هشتگ اختصاصی: {user['hashtag'] if user['hashtag'] else 'ثبت نشده'}
♥️ شکلک اختصاصی: {user['emoji'] if user['emoji'] else 'ثبت نشده'}
🐣 حیوان مورد علاقه‌ت: {pets_text}

--------------------------------------
::::: درگروه ::::

▪︎🏆 درجه شما در گروه:
▪︎💠 مقام شما در گروه:
"""
    bot.reply_to(message, text)

# --- دستورات افزودن و حذف ادمین ---
@bot.message_handler(commands=["admin", "dadmin", "ddadmin"])
def manage_admins(message):
    user_id = message.from_user.id
    if user_id != owner_id:
        bot.reply_to(message, "فقط مالک ربات می‌تواند این دستور را اجرا کند.")
        return

    args = message.text.split()
    cmd = message.text.split()[0]

    if cmd == "/admin":
        if not message.reply_to_message:
            bot.reply_to(message, "برای افزودن ادمین باید روی پیام شخص موردنظر ریپلای کنید.")
            return
        new_admin_id = message.reply_to_message.from_user.id
        admins.add(new_admin_id)
        bot.reply_to(message, f"کاربر {new_admin_id} به مدیران ربات افزوده شد.")
    elif cmd == "/dadmin":
        if not message.reply_to_message:
            bot.reply_to(message, "برای حذف ادمین باید روی پیام شخص موردنظر ریپلای کنید.")
            return
        rem_admin_id = message.reply_to_message.from_user.id
        if rem_admin_id in admins:
            admins.remove(rem_admin_id)
            bot.reply_to(message, f"کاربر {rem_admin_id} از مدیران ربات حذف شد.")
        else:
            bot.reply_to(message, "این کاربر ادمین نیست.")
    elif cmd == "/ddadmin":
        admins.clear()
        bot.reply_to(message, "تمام مدیران ربات حذف شدند.")

# --- ثبت تاریخ تولد با دستور /old ---
@bot.message_handler(regexp=r"^/old\s+(\d{4}/\d{1,2}/\d{1,2})$")
def set_birthday(message):
    user_id = message.from_user.id
    match = re.match(r"^/old\s+(\d{4}/\d{1,2}/\d{1,2})$", message.text)
    if not match:
        bot.reply_to(message, "فرمت تاریخ اشتباه است. مثال صحیح: /old 1370/1/11")
        return
    birthday = match.group(1)
    user = users[user_id]
    if user['coins'] < 25:
        bot.reply_to(message, "موجودی سکه شما کافی نیست برای ثبت تاریخ تولد.")
        return
    user['birthday'] = birthday
    user['coins'] -= 25
    bot.reply_to(message, f"تاریخ تولد شما با موفقیت ثبت شد: {birthday}\n۲۵ سکه از حسابتان کسر گردید.")

# --- ثبت هشتگ اختصاصی با دستور /mytag ---
@bot.message_handler(regexp=r"^/mytag\s+#\S+$")
def set_hashtag(message):
    user_id = message.from_user.id
    hashtag = message.text.split(maxsplit=1)[1]
    user = users[user_id]
    if user['coins'] < 80:
        bot.reply_to(message, "موجودی سکه شما کافی نیست برای ثبت هشتگ.")
        return
    user['hashtag'] = hashtag
    user['coins'] -= 80
    bot.reply_to(message, f"کاربر عزیز هشتگ {hashtag} شما با موفقیت ثبت شد و ۸۰ سکه از حساب شما کسر شد.")

# --- ثبت شکلک اختصاصی با دستور /emoji ---
@bot.message_handler(commands=["emoji"])
def set_emoji(message):
    user_id = message.from_user.id
    user = users[user_id]
    # برای سادگی اینجا فقط پیام بدیم، میتونیم دستور کامل تر بنویسیم بعدا
    bot.reply_to(message, "برای ثبت شکلک اختصاصی، لطفا دستور کامل را ارسال کنید یا این بخش را بعدا کامل میکنیم.")

# --- خرید حیوان خانگی و فروشگاه ---

pet_store = {
    "🐺": ("گرگ", 150),
    "🦁": ("شیر", 350),
    "🐉": ("اژدها", 400),
    "🐣": ("جوجه", 45),
    "🐰": ("خرگوش", 35),
    "🦊": ("روباه", 45),
    "🐱": ("گربه", 30),
    "🐶": ("سگ", 45),
    "🐪": ("شتر", 60),
    "🦌": ("گوزن", 30),
    "🦈": ("کوسه", 55),
    "🐆": ("پلنگ", 90)
}

@bot.message_handler(commands=["shop"])
def shop(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎂 ثبت تولد (۲۵ 🪙)", callback_data="set_birthday"),
        types.InlineKeyboardButton("🧿 خرید هشتگ (۸۰ 🪙)", callback_data="set_hashtag"),
        types.InlineKeyboardButton("🖼️ شکلک اختصاصی (۵۰ 🪙)", callback_data="set_emoji"),
        types.InlineKeyboardButton("🐾 خرید حیوان خانگی", callback_data="buy_pet"),
        types.InlineKeyboardButton("💠 قدرت ویژه (در حال ساخت)", callback_data="coming_soon"),
        types.InlineKeyboardButton("🚪 خروج از فروشگاه", callback_data="exit_shop")
    )
    bot.send_message(message.chat.id, "🛍️ خوش آمدی به فروشگاه فرم\nروی یکی از گزینه‌ها کلیک کن:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "buy_pet")
def pet_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for emoji, (name, price) in pet_store.items():
        markup.add(types.InlineKeyboardButton(f"{emoji} {name} ({price} 🪙)", callback_data=f"buy_{emoji}"))
    markup.add(types.InlineKeyboardButton("🚫 انصراف", callback_data="exit_shop"))
    bot.edit_message_text("🐾 لطفاً حیوان خانگی مورد علاقه‌تو انتخاب کن:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_pet_buy(call):
    user_id = call.from_user.id
    emoji = call.data.replace("buy_", "")
    if emoji in pet_store:
        name, cost = pet_store[emoji]
        if users[user_id]["coins"] >= cost:
            if emoji not in [e for e, n in users[user_id]["pets"]]:
                users[user_id]["coins"] -= cost
                users[user_id]["pets"].append((emoji, name))
                pets_text = " - ".join([f"{e} {n}" for e, n in users[user_id]["pets"]])
                bot.edit_message_text(f"{emoji} {name} با موفقیت خریداری شد!\n💰 {cost} سکه از حسابت کم شد.", call.message.chat.id, call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "این حیوان را قبلاً خریدی عزیزم 💕", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "سکه‌هات کافی نیست عشقم! 🥺", show_alert=True)

@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith("- "))
def remove_pet(msg):
    user_id = msg.from_user.id
    emoji = msg.text.replace("- ", "").strip()
    for e, name in users[user_id]["pets"]:
        if e == emoji:
            users[user_id]["pets"].remove((e, name))
            bot.reply_to(msg, f"{e} {name} با موفقیت از لیست حیوانات خانگی شما حذف گردید! 🥲")
            return
    bot.reply_to(msg, "این حیوان در لیست شما یافت نشد 😕")

# --- دستورات افزودن و کسر سکه و امتیاز ---
@bot.message_handler(func=lambda m: (is_admin(m.from_user.id) or m.from_user.id == owner_id) and m.reply_to_message and (m.text.startswith("+") or m.text.startswith("-")))
def add_remove_coins_points(message):
    try:
        text = message.text.strip()
        sign = text[0]
        parts = text[1:].strip().split()
        amount = int(parts[0])
        user_id = message.reply_to_message.from_user.id
        user = users[user_id]

        if sign == "+":
            if "🪙" in text:
                user["coins"] += amount
                bot.reply_to(message, f"💰 {amount} سکه به حساب کاربر {user_id} ({message.reply_to_message.from_user.username or 'ندارد'}) اضافه شد.")
            else:
                user["points"] += amount
                bot.reply_to(message, f"💎 {amount} امتیاز به حساب کاربر {user_id} ({message.reply_to_message.from_user.username or 'ندارد'}) اضافه شد.")
        elif sign == "-":
            if "🪙" in text:
                user["coins"] = max(0, user["coins"] - amount)
                bot.reply_to(message, f"💰 {amount} سکه از حساب کاربر {user_id} ({message.reply_to_message.from_user.username or 'ندارد'}) کسر شد.")
            else:
                user["points"] = max(0, user["points"] - amount)
                bot.reply_to(message, f"💎 {amount} امتیاز از حساب کاربر {user_id} ({message.reply_to_message.from_user.username or 'ندارد'}) کسر شد.")
    except Exception as e:
        bot.reply_to(message, "فرمت دستور اشتباه است یا مقدار عددی معتبر نیست.")

bot.infinity_polling()
