import telebot
from telebot import types
import sqlite3
import re
import time

TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkFWFs"
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
    spouse_id INTEGER,
    spouse_username TEXT,
    spouse_name TEXT,
    mehriye INTEGER DEFAULT 0
)
''')
conn.commit()

# دیکشنری موقت برای درخواست‌های عشق (proposer_id: target_id)
love_requests = {}

# افزودن کاربر جدید
def add_user(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username if message.from_user.username else "ندارد"

    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)", (user_id, name, username))
        conn.commit()

# دریافت نام و یوزرنیم کاربر بر اساس آیدی
def get_user_info(user_id):
    c.execute("SELECT name, username FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row:
        return row[0], row[1]
    return "ندارد", "ندارد"

# دستور /my برای نمایش پروفایل
@bot.message_handler(commands=['my'])
def show_profile(message):
    add_user(message)
    user_id = message.from_user.id
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    if data:
        tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"
        spouse_display = f"{data[7]} (@{data[8]})" if data[7] and data[8] else "ندارد"
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
😍 اسم همسر یا عشق‌ِت: {spouse_display}
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

# دستور /love برای ارسال درخواست عشق
@bot.message_handler(commands=['love'])
def love_request(message):
    add_user(message)
    if not message.reply_to_message:
        bot.reply_to(message, "❌ لطفاً روی پیام کسی که دوستش داری ریپلای کن و بعد دستور /love رو بزن.")
        return

    proposer_id = message.from_user.id
    target = message.reply_to_message.from_user

    if proposer_id == target.id:
        bot.reply_to(message, "😅 خودت رو که نمی‌تونی عاشق شی عزیزم!")
        return

    # چک کردن موجودی سکه پیشنهاددهنده (حداقل 500)
    c.execute("SELECT coin FROM users WHERE user_id = ?", (proposer_id,))
    row = c.fetchone()
    if not row or row[0] < 500:
        bot.reply_to(message, "❌ متأسفم، طرف پیشنهاد‌دهنده ۵۰۰ سکه برای درخواست ثبت عشق نداره! 🥲")
        return

    # ذخیره درخواست عشق در دیکشنری موقت
    love_requests[proposer_id] = target.id

    proposer_username = message.from_user.username if message.from_user.username else "ندارد"
    target_username = target.username if target.username else "ندارد"

    text = f"💘 اوه اوه! یه دل نه صد دل!  \n@{proposer_username} دلش بدجوری پیش @{target_username} گیر کرده! 😍  \n@{target_username} عزیز، اگه تو هم حسش رو داری، با یکی از این دستورها درخواستت رو قبول کن و مهریه سکه‌ات رو ثبت کن:\n" \
           f"- قبول با ۵۰۰ سکه مهریه: `/accept500`\n- قبول با ۱۰۰۰ سکه مهریه: `/accept1000`\n- قبول با ۲۰۰۰ سکه مهریه: `/accept2000`"

    bot.reply_to(message, text)

# دستور /accept برای قبول درخواست عشق با مهریه
@bot.message_handler(regexp=r'^/accept(500|1000|2000)$')
def accept_love(message):
    accepter_id = message.from_user.id
    c.execute("SELECT coin FROM users WHERE user_id = ?", (accepter_id,))
    row = c.fetchone()
    if not row:
        bot.reply_to(message, "❌ شما در دیتابیس ثبت نیستید!")
        return

    # چک کردن درخواست وجود دارد
    proposer_id = None
    for p_id, t_id in love_requests.items():
        if t_id == accepter_id:
            proposer_id = p_id
            break

    if proposer_id is None:
        bot.reply_to(message, "❌ کسی به شما پیشنهاد عشق نداده!")
        return

    mehriye = int(message.text[7:])  # عدد مهریه از دستور گرفته میشه
    # چک کردن مقدار مهریه صحیح است؟
    if mehriye not in (500, 1000, 2000):
        bot.reply_to(message, "❗ لطفاً مهریه را فقط یکی از اعداد ۵۰۰، ۱۰۰۰ یا ۲۰۰۰ وارد کنید.")
        return

    # چک کردن سکه پیشنهاد دهنده برای مهریه
    c.execute("SELECT coin FROM users WHERE user_id = ?", (proposer_id,))
    row = c.fetchone()
    if not row or row[0] < mehriye:
        bot.reply_to(message, f"❌ متأسفم، پیشنهاد‌دهنده {mehriye} سکه برای مهریه نداره! 🥲")
        love_requests.pop(proposer_id)
        return

    # کم کردن سکه مهریه از پیشنهاد دهنده
    c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (mehriye, proposer_id))
    # ثبت همسر و مهریه برای هر دو
    proposer_name, proposer_username = get_user_info(proposer_id)
    accepter_name, accepter_username = get_user_info(accepter_id)

    c.execute("""UPDATE users SET spouse_id=?, spouse_username=?, spouse_name=?, mehriye=? WHERE user_id=?""",
              (accepter_id, accepter_username, accepter_name, mehriye, proposer_id))
    c.execute("""UPDATE users SET spouse_id=?, spouse_username=?, spouse_name=?, mehriye=? WHERE user_id=?""",
              (proposer_id, proposer_username, proposer_name, mehriye, accepter_id))
    conn.commit()

    love_requests.pop(proposer_id)

    text = f"💞 عشقتون تأیید شد!  \n@{proposer_username} و @{accepter_username} حالا یک قلب شدن! 💕  \nمهریه سکه: {mehriye} سکه  \nبا آرزوی خوشبختی برای این زوج دوست‌داشتنی! 🥰"
    bot.reply_to(message, text)

# دستور /dlove برای جدایی
@bot.message_handler(commands=['dlove'])
def delete_love(message):
    user_id = message.from_user.id
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    else:
        # چک کردن اگر شناسه یا یوزرنیم در متن هست
        pattern = r'@(\w+)'
        match = re.search(pattern, message.text)
        if match:
            username = match.group(1)
            c.execute("SELECT user_id FROM users WHERE username = ?", (username,))
            res = c.fetchone()
            if res:
                target_id = res[0]
            else:
                bot.reply_to(message, "❌ کاربر مورد نظر یافت نشد!")
                return
        else:
            bot.reply_to(message, "❌ لطفاً ریپلای کنید یا یوزرنیم را وارد کنید.")
            return

    # بررسی عشق بین دو نفر
    c.execute("SELECT spouse_id, mehriye FROM users WHERE user_id = ?", (user_id,))
    row1 = c.fetchone()
    c.execute("SELECT spouse_id FROM users WHERE user_id = ?", (target_id,))
    row2 = c.fetchone()

    if not row1 or not row2 or row1[0] != target_id or row2[0] != user_id:
        bot.reply_to(message, "⚠️ شما با این فرد رابطه‌ای ندارید!")
        return

    mehriye = row1[1]

    # کم کردن مهریه از حساب پیشنهاد دهنده و اضافه به حساب قبول کننده
    c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (mehriye, user_id))
    c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (mehriye, target_id))

    # حذف عشق از دیتابیس (پاک کردن فیلدهای همسر و مهریه)
    c.execute("""UPDATE users SET spouse_id=NULL, spouse_username=NULL, spouse_name=NULL, mehriye=0 WHERE user_id IN (?, ?)""",
              (user_id, target_id))
    conn.commit()

    user_name, user_username = get_user_info(user_id)
    target_name, target_username = get_user_info(target_id)

    text = f"💔 عشق بین @{user_username} و @{target_username} به پایان رسید...\n💸 مهریه {mehriye} سکه به حساب @{target_username} واریز شد.\n🕊️ همیشه خوشحال باشین حتی اگه از هم جدا شدین."
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

# شروع ربات
bot.infinity_polling()
