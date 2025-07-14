import telebot
from telebot import types
import sqlite3
import re
import time

TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
OWNER_ID = 7341748124
bot = telebot.TeleBot(TOKEN)

# حذف webhook قبلی
bot.remove_webhook()
time.sleep(1)

# اتصال به دیتابیس
conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

# ایجاد جدول کاربران با ستون‌های جدید برای عشق (eshgh_name و eshgh_username)
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    coin INTEGER DEFAULT 180,
    score INTEGER DEFAULT 250,
    gold_tick INTEGER DEFAULT 0,
    eshgh_name TEXT DEFAULT NULL,
    eshgh_username TEXT DEFAULT NULL
)
''')
conn.commit()

# افزودن کاربر جدید
def add_user(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username if message.from_user.username else "ندارد"

    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)", (user_id, name, username))
        conn.commit()

# دستور /my برای نمایش پروفایل به همراه اطلاعات عشق
@bot.message_handler(commands=['my'])
def show_profile(message):
    add_user(message)
    user_id = message.from_user.id
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if data:
        tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"

        # نمایش عشق به همراه نام و یوزرنیم یا خالی اگر ندارد
        if data[6] and data[7]:
            eshgh_info = f"{data[6]} (@{data[7]})"
        else:
            eshgh_info = ""

        text = f'''
━━━【 پروفایل شما در گروه 】━━━

•مشخصات فردی شما•
👤 نام: {data[1]}
✨ یوزرنیم: @{data[2]} 
⚔️ آیدی عددی: {data[0]}

🌐 کشور شما: 🇮🇷 ایران
---------------------------
•• دارایی‌ها و امتیازت: ••
💰 سکه‌هات: {data[3]}
💎 امتیازت: {data[4]}
⚜️ نشان تایید طلایی: {tick}
---------------------------
•مشخصات خانواده شما•
😍 اسم همسر یا عشق‌ِت: {eshgh_info}
♥️ اسم فرزندتون: 
🐣 حیوان خانگی شما: 
♨️ فرقه‌ای که توش عضوی: 
---------------------------
🌙 شکلک اختصاصی: 
🎂 تاریخ تولدت: 
🔮 قدرت‌ها و طلسم‌ها: 
---------------------------
::::: در گروه :::::

▪︎🏆 درجه شما در گروه: 
▪︎💠 مقام شما در گروه: 
'''
        bot.reply_to(message, text)

# دستور /tik برای فعال‌سازی تیک طلایی
@bot.message_handler(commands=['tik'])
def give_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        uid = message.reply_to_message.from_user.id
        c.execute("UPDATE users SET gold_tick = 1 WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "⚜️ نشان تایید طلایی برای این کاربر فعال شد ✅")

# دستور /dtik برای حذف تیک طلایی
@bot.message_handler(commands=['dtik'])
def remove_tick(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        uid = message.reply_to_message.from_user.id
        c.execute("UPDATE users SET gold_tick = 0 WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "❌ نشان تایید طلایی از این کاربر برداشته شد.")

# مدیریت سکه و امتیاز با ریپلای
@bot.message_handler(func=lambda m: m.reply_to_message)
def control_points(message):
    if message.from_user.id != OWNER_ID:
        return
    uid = message.reply_to_message.from_user.id
    text = message.text.strip()

    # افزودن سکه
    if re.match(r'^\+ 🪙 \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💰 تعداد {amount} سکه به حساب <code>{uid}</code> اضافه شد!\n✨ ثروتت داره بیشتر میشه 😎", parse_mode="HTML")

    # کم کردن سکه
    elif re.match(r'^\- 🪙 \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💸 تعداد {amount} سکه از حساب <code>{uid}</code> کم شد!\nمراقب باش که صفر نشی! 🫣", parse_mode="HTML")

    # افزودن امتیاز
    elif re.match(r'^\+ \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"🎉 {amount} امتیاز به <code>{uid}</code> اضافه شد!\nدرخششت مبارک! 🌟", parse_mode="HTML")

    # کم کردن امتیاز
    elif re.match(r'^\- \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET score = score - ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💔 {amount} امتیاز از <code>{uid}</code> کم شد!\nولی نگران نباش، جبران میشه! 💪", parse_mode="HTML")

# دستور /love برای ثبت درخواست عشق
@bot.message_handler(commands=['love'])
def love_request(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ لطفا روی پیام فردی که دوست داری ریپلای کن و بعد دستور /love را بزن.")
        return
    proposer = message.from_user
    target = message.reply_to_message.from_user

    # بررسی اینکه پیشنهاددهنده خودش نیست
    if proposer.id == target.id:
        bot.reply_to(message, "❌ نمی‌تونی به خودت عشق بدی عزیزم!")
        return

    # چک کردن وجود هر دو در دیتابیس
    add_user(message)
    add_user(message.reply_to_message)

    # ارسال پیام عاشقانه با دکمه تایید به هدف
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❤️ قبول می‌کنم", callback_data=f"accept_love:{proposer.id}:{target.id}"))
    bot.send_message(message.chat.id,
                     f"💌 اووه! @{proposer.username} دلش برای @{target.username} تنگ شده و عاشقش شده! آیا تو هم موافقی؟ 💖",
                     reply_markup=markup)

# هندلر دکمه قبول عشق
@bot.callback_query_handler(func=lambda c: c.data.startswith("accept_love"))
def handle_accept_love(call):
    data = call.data.split(":")
    if len(data) != 3:
        return
    proposer_id = int(data[1])
    target_id = int(data[2])

    # فقط خود target اجازه داره قبول کنه
    if call.from_user.id != target_id:
        bot.answer_callback_query(call.id, "❌ فقط خودت می‌تونی این درخواست رو قبول کنی.")
        return

    # بررسی سکه‌ها و کسر ۵۰۰ سکه از proposer
    c.execute("SELECT coin FROM users WHERE user_id = ?", (proposer_id,))
    coin = c.fetchone()
    if not coin or coin[0] < 500:
        bot.answer_callback_query(call.id, "❌ عزیزم، ۵۰۰ سکه برای ثبت عشق لازم داری.")
        return

    c.execute("UPDATE users SET coin = coin - 500 WHERE user_id = ?", (proposer_id,))
    # ثبت عشق (نام و یوزرنیم پیشنهاددهنده و قبول‌کننده)
    c.execute("SELECT username, name FROM users WHERE user_id = ?", (proposer_id,))
    proposer_data = c.fetchone()
    c.execute("SELECT username, name FROM users WHERE user_id = ?", (target_id,))
    target_data = c.fetchone()

    # ثبت عشق در هر دو حساب
    c.execute("UPDATE users SET eshgh_username = ?, eshgh_name = ? WHERE user_id = ?", (target_data[0], target_data[1], proposer_id))
    c.execute("UPDATE users SET eshgh_username = ?, eshgh_name = ? WHERE user_id = ?", (proposer_data[0], proposer_data[1], target_id))
    conn.commit()

    bot.answer_callback_query(call.id, "💖 عشق شما ثبت شد، حالا مهریه‌ات رو مشخص کن...")

    # پیام درخواست مهریه
    bot.send_message(call.message.chat.id,
                     f"🌹 عزیزم @{target_data[0]}، حالا مهریه‌ات رو مشخص کن! لطفا یک عدد بفرست تا ثبت کنم...")

# دیکشنری برای نگهداری موقت درخواست مهریه {user_id: proposer_id}
pending_mahrieh = {}

@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def handle_mahrieh(message):
    user_id = message.from_user.id
    if user_id not in pending_mahrieh:
        return
    mahrieh = int(message.text)
    proposer_id = pending_mahrieh[user_id]

    # ذخیره مهریه (در اینجا فقط چاپ می‌کنیم چون هنوز دیتابیس مهریه رو نداریم)
    # در صورت نیاز باید جدول جدید ساخته شود و ذخیره کنیم
    bot.reply_to(message, f"✅ مهریه {mahrieh} سکه برای عشق‌تان ثبت شد!")

    # حذف از pending
    del pending_mahrieh[user_id]

# دستور /dlove برای درخواست جدایی
@bot.message_handler(commands=['dlove'])
def request_divorce(message):
    user_id = message.from_user.id
    # پیدا کردن هدف از ریپلای یا پارامتر بعد دستور
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ لطفا ریپلای کنید یا آیدی فرد را بعد دستور وارد کنید.")
            return
        username = args[1]
        if username.startswith('@'):
            username = username[1:]
        c.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if not row:
            bot.reply_to(message, "❌ کاربر پیدا نشد.")
            return
        target_user_id = row[0]
        # برای سادگی یک شیء user مجازی می‌سازیم
        target_user = types.User(id=target_user_id, is_bot=False, first_name="", username=username, last_name=None)

    # چک کنیم این دو نفر عشقی با هم دارن یا نه
    c.execute("SELECT eshgh_username FROM users WHERE user_id = ?", (user_id,))
    user_eshgh_username = c.fetchone()
    c.execute("SELECT username FROM users WHERE user_id = ?", (target_user.id,))
    target_username = c.fetchone()
    if not user_eshgh_username or not target_username or user_eshgh_username[0] != target_username[0]:
        bot.reply_to(message, "❌ شما و این شخص عشقی با هم ندارید که بخواهید جدا بشید.")
        return

    # ساخت پیام تایید جدایی با دکمه‌ها
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ بله، موافقم", callback_data=f"confirm_divorce:{user_id}:{target_user.id}"),
        types.InlineKeyboardButton("❌ نخیر، ادامه میدم", callback_data="cancel_divorce")
    )
    bot.send_message(message.chat.id,
                     f"💔 آیا واقعاً می‌خواهید از عشق خود با @{target_user.username} جدا شوید؟",
                     reply_markup=markup)

# هندلر callback دکمه‌ها برای جدایی
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_divorce") or call.data == "cancel_divorce")
def handle_divorce_callback(call):
    if call.data == "cancel_divorce":
        bot.answer_callback_query(call.id, "ادامه رابطه ثبت شد ❤️")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        return

    parts = call.data.split(":")
    if len(parts) != 3:
        return

    user1_id = int(parts[1])
    user2_id = int(parts[2])

    # فقط کسانی که درخواست دادن اجازه دارن تایید کنن
    if call.from_user.id != user1_id and call.from_user.id != user2_id:
        bot.answer_callback_query(call.id, "❌ شما اجازه انجام این کار را ندارید.")
        return

    # حذف عشق از دیتابیس
    c.execute("UPDATE users SET eshgh_username = NULL, eshgh_name = NULL WHERE user_id = ?", (user1_id,))
    c.execute("UPDATE users SET eshgh_username = NULL, eshgh_name = NULL WHERE user_id = ?", (user2_id,))

    # کسر 500 سکه از پیشنهاددهنده (user1_id)
    c.execute("UPDATE users SET coin = coin - 500 WHERE user_id = ?", (user1_id,))
    # اضافه کردن 500 سکه به قبول‌کننده (user2_id)
    c.execute("UPDATE users SET coin = coin + 500 WHERE user_id = ?", (user2_id,))
    conn.commit()

    # حذف پیام تایید
    bot.delete_message(call.message.chat.id, call.message.message_id)

    # ارسال پیام رمانتیک جدایی
    c.execute("SELECT username FROM users WHERE user_id = ?", (user1_id,))
    user1_username = c.fetchone()[0] or "ندارد"
    c.execute("SELECT username FROM users WHERE user_id = ?", (user2_id,))
    user2_username = c.fetchone()[0] or "ندارد"
    bot.send_message(call.message.chat.id,
                     f"💔 عشق بین @{user1_username} و @{user2_username} به پایان رسید...\n"
                     f"💸 ۵۰۰ سکه از حساب پیشنهاددهنده کسر و به قبول‌کننده واریز شد.")
    bot.answer_callback_query(call.id, "💔 جدایی با موفقیت ثبت شد.")

bot.infinity_polling()
