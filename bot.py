import telebot
from telebot import types
import sqlite3
import re
import time

TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
OWNER_ID = 7341748124
bot = telebot.TeleBot(TOKEN)

# حذف وب‌هوک قبلی برای جلوگیری از ارور 409
bot.remove_webhook()
time.sleep(1)

# اتصال به دیتابیس
conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

# ساخت جدول کاربران
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    coin INTEGER DEFAULT 180,
    score INTEGER DEFAULT 250,
    gold_tick INTEGER DEFAULT 0,
    eshgh_user_id INTEGER DEFAULT NULL,
    eshgh_username TEXT DEFAULT NULL,
    eshgh_name TEXT DEFAULT NULL,
    mehrieh INTEGER DEFAULT NULL
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

# دستور /my برای نمایش پروفایل
@bot.message_handler(commands=['my'])
def show_profile(message):
    add_user(message)
    user_id = message.from_user.id
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if data:
        tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"
        eshgh = f"@{data[7]}" if data[7] else "ندارد"
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
😍 اسم همسر یا عشق‌ِت: {eshgh}
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

# مدیریت سکه و امتیاز با ریپلای (فقط برای مالک)
@bot.message_handler(func=lambda m: m.reply_to_message is not None)
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

# =============== مدیریت عشق =================

# حافظه موقت برای درخواست‌های عشق {target_user_id: proposer_user_id}
pending_loves = {}

# متغیر برای ذخیره مهریه موقت
pending_mehrieh = {}

# دستور /love
@bot.message_handler(commands=['love'])
def love_request(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ لطفاً روی پیام کسی که دوستش داری ریپلای کن و بعد دستور /love رو بزن.")
        return

    proposer = message.from_user
    target = message.reply_to_message.from_user

    if proposer.id == target.id:
        bot.reply_to(message, "😅 به خودت که نمی‌تونی عشق بدی عزیزم!")
        return

    # ذخیره درخواست در حافظه موقت
    pending_loves[target.id] = proposer.id

    proposer_name = f"@{proposer.username}" if proposer.username else proposer.first_name
    target_name = f"@{target.username}" if target.username else target.first_name

    bot.send_message(message.chat.id,
        f"💘 وای وای وای! {proposer_name} به طور رسمی اعلام کرده که دلش پیش {target_name} گیره! 😳\n"
        f"{target_name} عزیز… می‌خوای این عشقو واقعی کنیم؟ فقط کافیه همین‌جا بنویسی /accept 💖"
    )

# دستور /accept
@bot.message_handler(commands=['accept'])
def accept_love(message):
    accepter = message.from_user
    accepter_id = accepter.id

    if accepter_id not in pending_loves:
        bot.reply_to(message, "❌ هیچ درخواستی برای شما ثبت نشده یا منقضی شده.")
        return

    proposer_id = pending_loves[accepter_id]

    c.execute("SELECT coin, username, name FROM users WHERE user_id = ?", (proposer_id,))
    proposer_data = c.fetchone()
    c.execute("SELECT username, name FROM users WHERE user_id = ?", (accepter_id,))
    accepter_data = c.fetchone()

    if not proposer_data or not accepter_data:
        bot.reply_to(message, "❌ مشکلی در اطلاعات کاربران پیش آمده.")
        return

    if proposer_data[0] < 500:
        bot.reply_to(message, "❌ کاربر پیشنهاددهنده سکه کافی برای ثبت عشق نداره!")
        return

    # ذخیره موقت مهریه
    pending_mehrieh[accepter_id] = {'proposer_id': proposer_id, 'chat_id': message.chat.id}

    bot.send_message(message.chat.id,
        f"🎉 واااای چه لحظه‌ای! عشق بین @{proposer_data[1]} و @{accepter_data[0]} با موفقیت ثبت شد! 💞\n"
        f"💸 ۵۰۰ سکه بابت این عشق سوزان از جیب پیشنهاددهنده کم شد...\n"
        f"حالا نوبت توئه عشقم! عدد مهریه‌ات رو همینجا برامون بفرست تا ثبتش کنم 🌹✨"
    )

    # کم کردن سکه پیشنهاددهنده
    c.execute("UPDATE users SET coin = coin - 500 WHERE user_id = ?", (proposer_id,))
    conn.commit()

    # حذف درخواست از pending_loves چون در مرحله مهریه هستیم
    del pending_loves[accepter_id]

# دریافت مهریه (عدد بین 100 تا 10000)
@bot.message_handler(func=lambda m: m.from_user.id in pending_mehrieh)
def receive_mehrieh(message):
    try:
        amount = int(message.text.strip())
    except:
        bot.reply_to(message, "❌ لطفاً فقط یک عدد صحیح وارد کن بین ۱۰۰ تا ۱۰,۰۰۰ سکه.")
        return

    if amount < 100 or amount > 10000:
        bot.reply_to(message, "❌ مهریه باید عددی بین ۱۰۰ تا ۱۰,۰۰۰ سکه باشه عزیزم! لطفاً دوباره انتخاب کن 🌹")
        return

    accepter_id = message.from_user.id
    proposer_id = pending_mehrieh[accepter_id]['proposer_id']
    chat_id = pending_mehrieh[accepter_id]['chat_id']

    pending_mehrieh[accepter_id]['amount'] = amount

    bot.send_message(chat_id,
        f"🔒 @{get_username(proposer_id)} عزیز! مهریه‌ای که عشقت برای این رابطه انتخاب کرده {amount} سکه‌ست 💰\n"
        f"آیا این عدد رو به عنوان مهر عشق‌تون قبول می‌کنی؟\n"
        f"برای تایید نهایی فقط کافیه همینجا بنویسی: /confirm ❤️"
    )

# دستور /confirm برای تایید نهایی مهریه توسط پیشنهاددهنده
@bot.message_handler(commands=['confirm'])
def confirm_mehrieh(message):
    proposer_id = message.from_user.id

    # جستجو در pending_mehrieh برای پیدا کردن قبول کننده مربوط به این پیشنهاددهنده
    accepter_id = None
    for aid, info in pending_mehrieh.items():
        if info['proposer_id'] == proposer_id and 'amount' in info:
            accepter_id = aid
            break

    if not accepter_id:
        bot.reply_to(message, "❌ درخواستی برای تایید مهریه ثبت نشده یا منقضی شده.")
        return

    amount = pending_mehrieh[accepter_id]['amount']
    chat_id = pending_mehrieh[accepter_id]['chat_id']

    # ثبت عشق نهایی در دیتابیس
    c.execute("UPDATE users SET eshgh_user_id = ?, eshgh_username = (SELECT username FROM users WHERE user_id = ?), eshgh_name = (SELECT name FROM users WHERE user_id = ?) WHERE user_id = ?", (accepter_id, accepter_id, accepter_id, proposer_id))
    c.execute("UPDATE users SET eshgh_user_id = ?, eshgh_username = (SELECT username FROM users WHERE user_id = ?), eshgh_name = (SELECT name FROM users WHERE user_id = ?), mehrieh = ? WHERE user_id = ?", (proposer_id, proposer_id, proposer_id, amount, accepter_id))
    conn.commit()

    bot.send_message(chat_id,
        f"💞 عشق بین @{get_username(proposer_id)} و @{get_username(accepter_id)} ثبت و نهایی شد! 🌹\n"
        f"مهریه {amount} سکه با توافق کامل تایید شد! 💍"
    )

    # حذف از pending_mehrieh
    del pending_mehrieh[accepter_id]

# دستور /dlove برای پایان دادن به عشق
@bot.message_handler(commands=['dlove'])
def delete_love(message):
    # چک می‌کنیم که یا ریپلای شده یا آیدی داده شده
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        # اگر آیدی یا یوزرنیم رو نوشتیم
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ لطفا یا روی پیام فرد مورد نظر ریپلای کن یا آیدی/یوزرنیمش رو بعد دستور بنویس.")
            return
        user_mention = args[1]
        if user_mention.startswith("@"):
            username = user_mention[1:]
            c.execute("SELECT user_id FROM users WHERE username = ?", (username,))
            res = c.fetchone()
            if not res:
                bot.reply_to(message, "❌ کاربر مورد نظر پیدا نشد.")
                return
            target_user = types.User(id=res[0], first_name=username, is_bot=False)  # ساخت کاربر موقت
        else:
            try:
                user_id = int(user_mention)
                c.execute("SELECT user_id, username FROM users WHERE user_id = ?", (user_id,))
                res = c.fetchone()
                if not res:
                    bot.reply_to(message, "❌ کاربر مورد نظر پیدا نشد.")
                    return
                target_user = types.User(id=res[0], first_name=res[1], is_bot=False)
            except:
                bot.reply_to(message, "❌ آیدی نامعتبر است.")
                return

    user1_id = message.from_user.id
    user2_id = target_user.id

    # بررسی اینکه عشق بین دو نفر ثبت شده یا نه
    c.execute("SELECT eshgh_user_id, mehrieh FROM users WHERE user_id = ?", (user1_id,))
    data1 = c.fetchone()
    c.execute("SELECT eshgh_user_id, mehrieh FROM users WHERE user_id = ?", (user2_id,))
    data2 = c.fetchone()

    if not data1 or not data2:
        bot.reply_to(message, "❌ اطلاعات کافی برای این کار موجود نیست.")
        return

    if (data1[0] != user2_id) and (data2[0] != user1_id):
        bot.reply_to(message, "❌ عشق ثبت شده‌ای بین شما دو نفر وجود ندارد.")
        return

    # مبلغ مهریه
    mehrieh_amount = data1[1] if data1[0] == user2_id else data2[1]

    if not mehrieh_amount:
        mehrieh_amount = 0

    # انتقال مهریه از پیشنهاددهنده به قبول کننده
    proposer_id = user1_id if data1[0] == user2_id else user2_id
    accepter_id = user2_id if proposer_id == user1_id else user1_id

    c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (mehrieh_amount, proposer_id))
    c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (mehrieh_amount, accepter_id))

    # پاک کردن عشق از دیتابیس
    c.execute("UPDATE users SET eshgh_user_id = NULL, eshgh_username = NULL, eshgh_name = NULL, mehrieh = NULL WHERE user_id IN (?, ?)", (user1_id, user2_id))
    conn.commit()

    # ارسال پیام در گروه
    proposer_username = get_username(proposer_id)
    accepter_username = get_username(accepter_id)

    bot.send_message(message.chat.id,
        f"💔 عشق بین @{proposer_username} و @{accepter_username} به پایان رسید...  \n"
        f"🪙 مهریه {mehrieh_amount} سکه از حساب پیشنهاددهنده کم و به عشق سابقش واریز شد.  \n"
        f"گاهی رفتن، تنها راهِ دوست داشتنه... 💫"
    )

# تابع کمکی برای گرفتن یوزرنیم از روی آیدی
def get_username(user_id):
    c.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    if res and res[0] and res[0] != "ندارد":
        return res[0]
    else:
        return str(user_id)

# شروع ربات
bot.infinity_polling()
