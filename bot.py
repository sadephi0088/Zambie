import telebot
from telebot import types
import sqlite3
import re

TOKEN = '7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs'  # توکن رباتت
OWNER_ID = 7341748124  # ایدی عددی خودت

bot = telebot.TeleBot(TOKEN)

اتصال به دیتابیس SQLite

conn = sqlite3.connect('botdata.db', check_same_thread=False)
cursor = conn.cursor()

ایجاد جدول‌ها اگر وجود نداشته باشند

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
name TEXT,
username TEXT,
country TEXT DEFAULT '🇮🇷 ایران',
coins INTEGER DEFAULT 180,
points INTEGER DEFAULT 200,
gold_badge INTEGER DEFAULT 0,
birthdate TEXT,
hashtag TEXT,
emoji TEXT,
pet TEXT,
rank TEXT,
position TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
user_id INTEGER PRIMARY KEY
)''')

conn.commit()

متغیر برای شمردن تعداد پیام هر کاربر جهت امتیازدهی

message_counts = {}
pm_awarding_active = True  # وضعیت فعال بودن امتیازدهی پیام

def is_admin(user_id):
if user_id == OWNER_ID:
return True
cursor.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,))
return cursor.fetchone() is not None

def get_user(user_id):
cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
return cursor.fetchone()

def add_user_if_not_exist(user):
cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,))
if cursor.fetchone() is None:
cursor.execute(
"INSERT INTO users(user_id, name, username) VALUES (?, ?, ?)",
(user.id, user.first_name, '@' + user.username if user.username else None))
conn.commit()

def update_user_field(user_id, field, value):
cursor.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
conn.commit()

def add_coins(user_id, amount):
cursor.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
row = cursor.fetchone()
if row:
new_coins = max(0, row[0] + amount)
cursor.execute("UPDATE users SET coins=? WHERE user_id=?", (new_coins, user_id))
conn.commit()
return new_coins
return None

def add_points(user_id, amount):
cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
row = cursor.fetchone()
if row:
new_points = max(0, row[0] + amount)
cursor.execute("UPDATE users SET points=? WHERE user_id=?", (new_points, user_id))
conn.commit()
return new_points
return None

def get_user_profile_text(user_id):
user = get_user(user_id)
if not user:
return "کاربر یافت نشد."
# user schema:
# (user_id, name, username, country, coins, points, gold_badge, birthdate, hashtag, emoji, pet, rank, position)
name = user[1] or ""
username = user[2] or "ندارد"
country = user[3] or "🇮🇷 ایران"
coins = user[4] or 0
points = user[5] or 0
gold_badge = user[6] or 0
birthdate = user[7] or ""
hashtag = user[8] or ""
emoji = user[9] or ""
pet = user[10] or ""
rank = user[11] or ""
position = user[12] or ""

badge_text = "✅" if gold_badge else "❌"  

profile_text = f"""━━━【 پروفایل شما در گروه 】━━━

•اطلاعات حقیقی•
👤 نام: {name}
✨ یوزرنیم: {username}
⚔️ ایدی عددی: {user_id}

🌐‌ کشور شما: {country}

•• دارایی شما: ••
💰 سکه‌هات: {coins}
💎 امتیازت: {points}
⚜️ نشان تایید طلایی: {badge_text}

🔮 قدرت‌ها و طلسم‌ها:
🎂 تاریخ تولدت: {birthdate}
♨️ هشتگ اختصاصی: {hashtag}
♥️ شکلک اختصاصی: {emoji}
🐣 حیوان مورد علاقه‌ت: {pet}

:: در گروه ::::

▪︎🏆 درجه شما در گروه: {rank}
▪︎💠 مقام شما در گروه: {position}
"""
return profile_text

دریافت نام کشور به صورت پیش‌فرض ایران

def get_country(user_id):
return "🇮🇷 ایران"

حذف webhook برای جلوگیری از خطای 409 هنگام polling

def remove_webhook():
bot.remove_webhook()

remove_webhook()

دستور شروع برای خوشامدگویی ساده (بعداً تکمیل می‌کنیم)

@bot.message_handler(commands=['start'])
def start_handler(message):
add_user_if_not_exist(message.from_user)
bot.reply_to(message, f"سلام {message.from_user.first_name} عزیز! خوش آمدی به ربات ما. برای مشاهده پروفایلت دستور /my را بفرست.")

دستور /my برای نمایش پروفایل خود کاربر یا کاربر ریپلای شده (برای مدیران و مالک)

@bot.message_handler(commands=['my'])
def my_profile_handler(message):
add_user_if_not_exist(message.from_user)
target_id = message.from_user.id
if message.reply_to_message:
target_id = message.reply_to_message.from_user.id
elif len(message.text.split()) > 1:
# امکان استفاده از آیدی عددی بعد از /my
parts = message.text.split()
if parts[1].isdigit():
target_id = int(parts[1])
if not is_admin(message.from_user.id) and target_id != message.from_user.id:
bot.reply_to(message, "⚠️ فقط مدیران و مالک ربات می‌توانند پروفایل دیگران را ببینند.")
return
add_user_if_not_exist(message.from_user)
profile = get_user_profile_text(target_id)
bot.send_message(message.chat.id, profile)

ثبت تاریخ تولد با دستور /old 1370/1/11

@bot.message_handler(regexp=r'^/old (\d{4}/\d{1,2}/\d{1,2})$')
def register_birthdate(message):
user_id = message.from_user.id
add_user_if_not_exist(message.from_user)
text = message.text.strip()
m = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', text)
if not m:
bot.reply_to(message, "فرمت تاریخ اشتباه است. باید مانند مثال زیر باشد:\n/old 1370/1/11")
return
birthdate = m.group(1)
# کسر 25 سکه
coins = add_coins(user_id, -25)
if coins is None or coins < 0:
bot.reply_to(message, "سکه کافی برای ثبت تاریخ تولد ندارید!")
add_coins(user_id, 25)  # بازگرداندن سکه چون کافی نبود
return
update_user_field(user_id, 'birthdate', birthdate)
bot.reply_to(message, f"🎉 تاریخ تولد شما با موفقیت ثبت شد: {birthdate}\nاز حساب شما 25 سکه کسر گردید.")

ثبت هشتگ اختصاصی با /mytag #قدرت

@bot.message_handler(regexp=r'^/mytag (#[\w\u0600-\u06FF]+)$')
def register_hashtag(message):
user_id = message.from_user.id
add_user_if_not_exist(message.from_user)
text = message.text.strip()
m = re.match(r'^/mytag (#[\w\u0600-\u06FF]+)$', text)
if not m:
bot.reply_to(message, "فرمت هشتگ اشتباه است. باید مانند مثال زیر باشد:\n/mytag #قدرت")
return
hashtag = m.group(1)
price = 80
coins = add_coins(user_id, -price)
if coins is None or coins < 0:
bot.reply_to(message, "سکه کافی برای ثبت هشتگ ندارید!")
add_coins(user_id, price)  # بازگرداندن سکه
return
update_user_field(user_id, 'hashtag', hashtag)
bot.reply_to(message, f"✨ هشتگ {hashtag} شما با موفقیت ثبت شد و {price} سکه از حساب شما کسر شد.")

ثبت شکلک اختصاصی با دستور /emoji 😊

@bot.message_handler(regexp=r'^/emoji (.+)$')
def register_emoji(message):
user_id = message.from_user.id
add_user_if_not_exist(message.from_user)
emoji = message.text.split(' ',1)[1]
price = 50
coins = add_coins(user_id, -price)
if coins is None or coins < 0:
bot.reply_to(message, "سکه کافی برای ثبت شکلک اختصاصی ندارید!")
add_coins(user_id, price)
return
update_user_field(user_id, 'emoji', emoji)
bot.reply_to(message, f"😍 شکلک اختصاصی شما ثبت شد و {price} سکه از حساب شما کسر گردید.")

خرید حیوان خانگی در /shop (قیمت‌ها)

pets_prices = {
"گرگ 🐺": 150,
"شیر 🦁": 350,
"اژدها 🐉": 400,
"جوجه 🐥": 45,
"خرگوش 🐇": 35,
"روباه 🦊": 45,
"گربه 🐱": 30,
"سگ 🐕": 45,
"شتر 🐫": 60,
"گوزن 🦌": 30,
"کوسه 🦈": 55,
"پلنگ 🐆": 90
}

دستور فروشگاه با دکمه‌ها

@bot.message_handler(commands=['shop'])
def shop_handler(message):
user_id = message.from_user.id
add_user_if_not_exist(message.from_user)

markup = types.InlineKeyboardMarkup(row_width=2)  
for pet, price in pets_prices.items():  
    markup.add(types.InlineKeyboardButton(f"{pet} — قیمت: {price} 🪙", callback_data=f"buy_pet|{pet}"))  
markup.add(types.InlineKeyboardButton("ثبت تاریخ تولد 🎂 — قیمت: 25 🪙", callback_data="buy_birthdate"))  
markup.add(types.InlineKeyboardButton("ثبت هشتگ اختصاصی ♨️ — قیمت: 80 🪙", callback_data="buy_hashtag"))  
markup.add(types.InlineKeyboardButton("ثبت شکلک اختصاصی ♥️ — قیمت: 50 🪙", callback_data="buy_emoji"))  
bot.send_message(message.chat.id, "🎁 فروشگاه ربات: محصولات زیر را می‌توانید بخرید:", reply_markup=markup)

هندلر کال‌بک‌ها برای خرید

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
user_id = call.from_user.id
add_user_if_not_exist(call.from_user)
data = call.data

if data.startswith("buy_pet|"):  
    pet_name = data.split("|")[1]  
    price = pets_prices.get(pet_name, None)  
    if price is None:  
        bot.answer_callback_query(call.id, "این حیوان موجود نیست.")  
        return  
    coins = add_coins(user_id, -price)  
    if coins is None or coins < 0:  
        add_coins(user_id, price)  # برگشت سکه  
        bot.answer_callback_query(call.id, "سکه کافی برای خرید این حیوان ندارید!")  
        return  
    # اضافه کردن حیوان به فرم  
    cursor.execute("SELECT pet FROM users WHERE user_id=?", (user_id,))  
    current_pets = cursor.fetchone()[0]  
    if current_pets:  
        new_pets = current_pets + " - " + pet_name  
    else:  
        new_pets = pet_name  
    update_user_field(user_id, 'pet', new_pets)  
    bot.answer_callback_query(call.id, f"🎉 حیوان {pet_name} با موفقیت خریداری شد!")  
    bot.send_message(call.message.chat.id, f"🎉 حیوان {pet_name} به پروفایل شما اضافه شد و {price} سکه از حساب شما کسر گردید.")  

elif data == "buy_birthdate":  
    bot.send_message(user_id, "لطفاً تاریخ تولد خود را به صورت زیر وارد کنید و ارسال کنید:\nمثال:\n/old 1370/1/11\n\nتوجه: ثبت تاریخ تولد ۲۵ سکه هزینه دارد.")  
    bot.answer_callback_query(call.id, "دستور ثبت تاریخ تولد به پیوی شما ارسال شد.")  

elif data == "buy_hashtag":  
    bot.send_message(user_id, "لطفاً هشتگ خود را به صورت زیر وارد کنید و ارسال کنید:\nمثال:\n/mytag #قدرت\n\nتوجه: ثبت هشتگ ۸۰ سکه هزینه دارد.")  
    bot.answer_callback_query(call.id, "دستور ثبت هشتگ به پیوی شما ارسال شد.")  

elif data == "buy_emoji":  
    bot.send_message(user_id, "لطفاً شکلک اختصاصی خود را به صورت زیر وارد کنید و ارسال کنید:\nمثال:\n/emoji 😊\n\nتوجه: ثبت شکلک اختصاصی ۵۰ سکه هزینه دارد.")  
    bot.answer_callback_query(call.id, "دستور ثبت شکلک اختصاصی به پیوی شما ارسال شد.")

حذف حیوان با دستور - 🐫

@bot.message_handler(regexp=r'^- (.+)$')
def remove_pet_handler(message):
user_id = message.from_user.id
add_user_if_not_exist(message.from_user)
pet_to_remove = message.text[2:].strip()
cursor.execute("SELECT pet FROM users WHERE user_id=?", (user_id,))
pets = cursor.fetchone()[0]
if not pets:
bot.reply_to(message, "شما هیچ حیوانی ندارید که حذف کنید.")
return
pet_list = [p.strip() for p in pets.split(" - ")]
if pet_to_remove not in pet_list:
bot.reply_to(message, f"حیوان {pet_to_remove} در پروفایل شما یافت نشد.")
return
pet_list.remove(pet_to_remove)
new_pets = " - ".join(pet_list) if pet_list else ""
update_user_field(user_id, 'pet', new_pets)
bot.reply_to(message, f"حیوان {pet_to_remove} با موفقیت از لیست جانوران خانگی شما حذف گردید! 🥲")

افزودن و حذف ادمین

@bot.message_handler(commands=['admin', 'dadmin', 'ddadmin'])
def admin_commands(message):
user_id = message.from_user.id
if user_id != OWNER_ID:
bot.reply_to(message, "⚠️ فقط مالک ربات می‌تواند این دستورات را اجرا کند.")
return
cmd = message.text.split()[0]
if not message.reply_to_message:
bot.reply_to(message, "⚠️ باید روی پیام شخص مورد نظر ریپلای کنید.")
return
target_id = message.reply_to_message.from_user.id
if cmd == '/admin':
cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (target_id,))
conn.commit()
bot.reply_to(message, f"✅ کاربر با ایدی {target_id} به مدیران ربات افزوده شد.")
elif cmd == '/dadmin':
cursor.execute("DELETE FROM admins WHERE user_id=?", (target_id,))
conn.commit()
bot.reply_to(message, f"✅ کاربر با ایدی {target_id} از مدیران ربات حذف شد.")
elif cmd == '/ddadmin':
cursor.execute("DELETE FROM admins")
conn.commit()
bot.reply_to(message, "✅ تمام مدیران ربات حذف شدند.")

اضافه و کم کردن سکه و امتیاز

@bot.message_handler(regexp=r'^(+|-)\s*(\d+)\s*(🪙)?$')
def add_subtract_coins_points(message):
user_id = message.from_user.id
if not is_admin(user_id):
bot.reply_to(message, "⚠️ فقط مدیران و مالک ربات می‌توانند از این دستور استفاده کنند.")
return
if not message.reply_to_message:
bot.reply_to(message, "⚠️ برای اضافه یا کسر کردن باید روی پیام فرد مورد نظر ریپلای کنید.")
return
target_id = message.reply_to_message.from_user.id
text = message.text.strip()
m = re.match(r'^(+|-)\s*(\d+)\s*(🪙)?$', text)
if not m:
bot.reply_to(message, "فرمت دستور اشتباه است.")
return
sign = m.group(1)
amount = int(m.group(2))
is_coin = m.group(3) == '🪙'  # اگر بود یعنی سکه، اگر نبود یعنی امتیاز

if is_coin:  
    if sign == '+':  
        new_coins = add_coins(target_id, amount)  
        bot.reply_to(message, f"🎉 {amount} سکه به کاربر {target_id} اضافه شد! 🪙")  
    else:  
        new_coins = add_coins(target_id, -amount)  
        bot.reply_to(message, f"⚠️ {amount} سکه از کاربر {target_id} کسر شد! 🪙")  
else:  
    if sign == '+':  
        new_points = add_points(target_id, amount)  
        bot.reply_to(message, f"🎉 {amount} امتیاز به کاربر {target_id} اضافه شد! 💎")  
    else:  
        new_points = add_points(target_id, -amount)  
        bot.reply_to(message, f"⚠️ {amount} امتیاز از کاربر {target_id} کسر شد! 💎")

امتیازدهی با هر 4 پیام (سکه نه، فقط امتیاز)

@bot.message_handler(func=lambda message: True)
def message_counter(message):
global message_counts, pm_awarding_active
user_id = message.from_user.id
add_user_if_not_exist(message.from_user)

if not pm_awarding_active:  
    return  

if user_id not in message_counts:  
    message_counts[user_id] = 1  
else:  
    message_counts[user_id] += 1  

if message_counts[user_id] >= 4:  
    add_points(user_id, 1)  
    message_counts[user_id] = 0  
    # ربات چیزی نمی‌فرسته، فقط امتیاز میده

دستور روشن و خاموش کردن امتیازدهی پیام

@bot.message_handler(commands=['offpm'])
def disable_pm_award(message):
global pm_awarding_active
if not is_admin(message.from_user.id):
return
pm_awarding_active = False
bot.reply_to(message, "✅ سیستم امتیازدهی با پیام خاموش شد.")

@bot.message_handler(commands=['onpm'])
def enable_pm_award(message):
global pm_awarding_active
if not is_admin(message.from_user.id):
return
pm_awarding_active = True
bot.reply_to(message, "✅ سیستم امتیازدهی با پیام فعال شد.")

اجرای ربات

bot.infinity_polling()

:: در گروه ::::  
  
▪︎🏆 درجه شما در گروه: {rank}  
▪︎💠 مقام شما در گروه: {position}  
"""  
    return profile_text  
  
# دریافت نام کشور به صورت پیش‌فرض ایران  
def get_country(user_id):  
    return "🇮🇷 ایران"  
  
# حذف webhook برای جلوگیری از خطای 409 هنگام polling  
def remove_webhook():  
    bot.remove_webhook()  
  
remove_webhook()  
  
# دستور شروع برای خوشامدگویی ساده (بعداً تکمیل می‌کنیم)  
@bot.message_handler(commands=['start'])  
def start_handler(message):  
    add_user_if_not_exist(message.from_user)  
    bot.reply_to(message, f"سلام {message.from_user.first_name} عزیز! خوش آمدی به ربات ما. برای مشاهده پروفایلت دستور /my را بفرست.")  
  
# دستور /my برای نمایش پروفایل خود کاربر یا کاربر ریپلای شده (برای مدیران و مالک)  
@bot.message_handler(commands=['my'])  
def my_profile_handler(message):  
    add_user_if_not_exist(message.from_user)  
    target_id = message.from_user.id  
    if message.reply_to_message:  
        target_id = message.reply_to_message.from_user.id  
    elif len(message.text.split()) > 1:  
        # امکان استفاده از آیدی عددی بعد از /my  
        parts = message.text.split()  
        if parts[1].isdigit():  
            target_id = int(parts[1])  
    if not is_admin(message.from_user.id) and target_id != message.from_user.id:  
        bot.reply_to(message, "⚠️ فقط مدیران و مالک ربات می‌توانند پروفایل دیگران را ببینند.")  
        return  
    add_user_if_not_exist(message.from_user)  
    profile = get_user_profile_text(target_id)  
    bot.send_message(message.chat.id, profile)  
  
# ثبت تاریخ تولد با دستور /old 1370/1/11  
@bot.message_handler(regexp=r'^/old (\d{4}/\d{1,2}/\d{1,2})$')  
def register_birthdate(message):  
    user_id = message.from_user.id  
    add_user_if_not_exist(message.from_user)  
    text = message.text.strip()  
    m = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', text)  
    if not m:  
        bot.reply_to(message, "فرمت تاریخ اشتباه است. باید مانند مثال زیر باشد:\n/old 1370/1/11")  
        return  
    birthdate = m.group(1)  
    # کسر 25 سکه  
    coins = add_coins(user_id, -25)  
    if coins is None or coins < 0:  
        bot.reply_to(message, "سکه کافی برای ثبت تاریخ تولد ندارید!")  
        add_coins(user_id, 25)  # بازگرداندن سکه چون کافی نبود  
        return  
    update_user_field(user_id, 'birthdate', birthdate)  
    bot.reply_to(message, f"🎉 تاریخ تولد شما با موفقیت ثبت شد: {birthdate}\nاز حساب شما 25 سکه کسر گردید.")  
  
# ثبت هشتگ اختصاصی با /mytag #قدرت  
@bot.message_handler(regexp=r'^/mytag (#[\w\u0600-\u06FF]+)$')  
def register_hashtag(message):  
    user_id = message.from_user.id  
    add_user_if_not_exist(message.from_user)  
    text = message.text.strip()  
    m = re.match(r'^/mytag (#[\w\u0600-\u06FF]+)$', text)  
    if not m:  
        bot.reply_to(message, "فرمت هشتگ اشتباه است. باید مانند مثال زیر باشد:\n/mytag #قدرت")  
        return  
    hashtag = m.group(1)  
    price = 80  
    coins = add_coins(user_id, -price)  
    if coins is None or coins < 0:  
        bot.reply_to(message, "سکه کافی برای ثبت هشتگ ندارید!")  
        add_coins(user_id, price)  # بازگرداندن سکه  
        return  
    update_user_field(user_id, 'hashtag', hashtag)  
    bot.reply_to(message, f"✨ هشتگ {hashtag} شما با موفقیت ثبت شد و {price} سکه از حساب شما کسر شد.")  
  
# ثبت شکلک اختصاصی با دستور /emoji 😊  
@bot.message_handler(regexp=r'^/emoji (.+)$')  
def register_emoji(message):  
    user_id = message.from_user.id  
    add_user_if_not_exist(message.from_user)  
    emoji = message.text.split(' ',1)[1]  
    price = 50  
    coins = add_coins(user_id, -price)  
    if coins is None or coins < 0:  
        bot.reply_to(message, "سکه کافی برای ثبت شکلک اختصاصی ندارید!")  
        add_coins(user_id, price)  
        return  
    update_user_field(user_id, 'emoji', emoji)  
    bot.reply_to(message, f"😍 شکلک اختصاصی شما ثبت شد و {price} سکه از حساب شما کسر گردید.")  
  
# خرید حیوان خانگی در /shop (قیمت‌ها)  
pets_prices = {  
    "گرگ 🐺": 150,  
    "شیر 🦁": 350,  
    "اژدها 🐉": 400,  
    "جوجه 🐥": 45,  
    "خرگوش 🐇": 35,  
    "روباه 🦊": 45,  
    "گربه 🐱": 30,  
    "سگ 🐕": 45,  
    "شتر 🐫": 60,  
    "گوزن 🦌": 30,  
    "کوسه 🦈": 55,  
    "پلنگ 🐆": 90  
}  
  
# دستور فروشگاه با دکمه‌ها  
@bot.message_handler(commands=['shop'])  
def shop_handler(message):  
    user_id = message.from_user.id  
    add_user_if_not_exist(message.from_user)  
  
    markup = types.InlineKeyboardMarkup(row_width=2)  
    for pet, price in pets_prices.items():  
        markup.add(types.InlineKeyboardButton(f"{pet} — قیمت: {price} 🪙", callback_data=f"buy_pet|{pet}"))  
    markup.add(types.InlineKeyboardButton("ثبت تاریخ تولد 🎂 — قیمت: 25 🪙", callback_data="buy_birthdate"))  
    markup.add(types.InlineKeyboardButton("ثبت هشتگ اختصاصی ♨️ — قیمت: 80 🪙", callback_data="buy_hashtag"))  
    markup.add(types.InlineKeyboardButton("ثبت شکلک اختصاصی ♥️ — قیمت: 50 🪙", callback_data="buy_emoji"))  
    bot.send_message(message.chat.id, "🎁 فروشگاه ربات: محصولات زیر را می‌توانید بخرید:", reply_markup=markup)  
  
# هندلر کال‌بک‌ها برای خرید  
@bot.callback_query_handler(func=lambda call: True)  
def callback_query(call):  
    user_id = call.from_user.id  
    add_user_if_not_exist(call.from_user)  
    data = call.data  
  
    if data.startswith("buy_pet|"):  
        pet_name = data.split("|")[1]  
        price = pets_prices.get(pet_name, None)  
        if price is None:  
            bot.answer_callback_query(call.id, "این حیوان موجود نیست.")  
            return  
        coins = add_coins(user_id, -price)  
        if coins is None or coins < 0:  
            add_coins(user_id, price)  # برگشت سکه  
            bot.answer_callback_query(call.id, "سکه کافی برای خرید این حیوان ندارید!")  
            return  
        # اضافه کردن حیوان به فرم  
        cursor.execute("SELECT pet FROM users WHERE user_id=?", (user_id,))  
        current_pets = cursor.fetchone()[0]  
        if current_pets:  
            new_pets = current_pets + " - " + pet_name  
        else:  
            new_pets = pet_name  
        update_user_field(user_id, 'pet', new_pets)  
        bot.answer_callback_query(call.id, f"🎉 حیوان {pet_name} با موفقیت خریداری شد!")  
        bot.send_message(call.message.chat.id, f"🎉 حیوان {pet_name} به پروفایل شما اضافه شد و {price} سکه از حساب شما کسر گردید.")  
  
    elif data == "buy_birthdate":  
        bot.send_message(user_id, "لطفاً تاریخ تولد خود را به صورت زیر وارد کنید و ارسال کنید:\nمثال:\n/old 1370/1/11\n\nتوجه: ثبت تاریخ تولد ۲۵ سکه هزینه دارد.")  
        bot.answer_callback_query(call.id, "دستور ثبت تاریخ تولد به پیوی شما ارسال شد.")  
  
    elif data == "buy_hashtag":  
        bot.send_message(user_id, "لطفاً هشتگ خود را به صورت زیر وارد کنید و ارسال کنید:\nمثال:\n/mytag #قدرت\n\nتوجه: ثبت هشتگ ۸۰ سکه هزینه دارد.")  
        bot.answer_callback_query(call.id, "دستور ثبت هشتگ به پیوی شما ارسال شد.")  
  
    elif data == "buy_emoji":  
        bot.send_message(user_id, "لطفاً شکلک اختصاصی خود را به صورت زیر وارد کنید و ارسال کنید:\nمثال:\n/emoji 😊\n\nتوجه: ثبت شکلک اختصاصی ۵۰ سکه هزینه دارد.")  
        bot.answer_callback_query(call.id, "دستور ثبت شکلک اختصاصی به پیوی شما ارسال شد.")  
  
# حذف حیوان با دستور - 🐫  
@bot.message_handler(regexp=r'^- (.+)$')  
def remove_pet_handler(message):  
    user_id = message.from_user.id  
    add_user_if_not_exist(message.from_user)  
    pet_to_remove = message.text[2:].strip()  
    cursor.execute("SELECT pet FROM users WHERE user_id=?", (user_id,))  
    pets = cursor.fetchone()[0]  
    if not pets:  
        bot.reply_to(message, "شما هیچ حیوانی ندارید که حذف کنید.")  
        return  
    pet_list = [p.strip() for p in pets.split(" - ")]  
    if pet_to_remove not in pet_list:  
        bot.reply_to(message, f"حیوان {pet_to_remove} در پروفایل شما یافت نشد.")  
        return  
    pet_list.remove(pet_to_remove)  
    new_pets = " - ".join(pet_list) if pet_list else ""  
    update_user_field(user_id, 'pet', new_pets)  
    bot.reply_to(message, f"حیوان {pet_to_remove} با موفقیت از لیست جانوران خانگی شما حذف گردید! 🥲")  
  
# افزودن و حذف ادمین  
@bot.message_handler(commands=['admin', 'dadmin', 'ddadmin'])  
def admin_commands(message):  
    user_id = message.from_user.id  
    if user_id != OWNER_ID:  
        bot.reply_to(message, "⚠️ فقط مالک ربات می‌تواند این دستورات را اجرا کند.")  
        return  
    cmd = message.text.split()[0]  
    if not message.reply_to_message:  
        bot.reply_to(message, "⚠️ باید روی پیام شخص مورد نظر ریپلای کنید.")  
        return  
    target_id = message.reply_to_message.from_user.id  
    if cmd == '/admin':  
        cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (target_id,))  
        conn.commit()  
        bot.reply_to(message, f"✅ کاربر با ایدی {target_id} به مدیران ربات افزوده شد.")  
    elif cmd == '/dadmin':  
        cursor.execute("DELETE FROM admins WHERE user_id=?", (target_id,))  
        conn.commit()  
        bot.reply_to(message, f"✅ کاربر با ایدی {target_id} از مدیران ربات حذف شد.")  
    elif cmd == '/ddadmin':  
        cursor.execute("DELETE FROM admins")  
        conn.commit()  
        bot.reply_to(message, "✅ تمام مدیران ربات حذف شدند.")  
  
# اضافه و کم کردن سکه و امتیاز  
@bot.message_handler(regexp=r'^(\+|\-)\s*(\d+)\s*(🪙)?$')  
def add_subtract_coins_points(message):  
    user_id = message.from_user.id  
    if not is_admin(user_id):  
        bot.reply_to(message, "⚠️ فقط مدیران و مالک ربات می‌توانند از این دستور استفاده کنند.")  
        return  
    if not message.reply_to_message:  
        bot.reply_to(message, "⚠️ برای اضافه یا کسر کردن باید روی پیام فرد مورد نظر ریپلای کنید.")  
        return  
    target_id = message.reply_to_message.from_user.id  
    text = message.text.strip()  
    m = re.match(r'^(\+|\-)\s*(\d+)\s*(🪙)?$', text)  
    if not m:  
        bot.reply_to(message, "فرمت دستور اشتباه است.")  
        return  
    sign = m.group(1)  
    amount = int(m.group(2))  
    is_coin = m.group(3) == '🪙'  # اگر بود یعنی سکه، اگر نبود یعنی امتیاز  
  
    if is_coin:  
        if sign == '+':  
            new_coins = add_coins(target_id, amount)  
            bot.reply_to(message, f"🎉 {amount} سکه به کاربر {target_id} اضافه شد! 🪙")  
        else:  
            new_coins = add_coins(target_id, -amount)  
            bot.reply_to(message, f"⚠️ {amount} سکه از کاربر {target_id} کسر شد! 🪙")  
    else:  
        if sign == '+':  
            new_points = add_points(target_id, amount)  
            bot.reply_to(message, f"🎉 {amount} امتیاز به کاربر {target_id} اضافه شد! 💎")  
        else:  
            new_points = add_points(target_id, -amount)  
            bot.reply_to(message, f"⚠️ {amount} امتیاز از کاربر {target_id} کسر شد! 💎")  
  
# امتیازدهی با هر 4 پیام (سکه نه، فقط امتیاز)  
@bot.message_handler(func=lambda message: True)  
def message_counter(message):  
    global message_counts, pm_awarding_active  
    user_id = message.from_user.id  
    add_user_if_not_exist(message.from_user)  
  
    if not pm_awarding_active:  
        return  
  
    if user_id not in message_counts:  
        message_counts[user_id] = 1  
    else:  
        message_counts[user_id] += 1  
  
    if message_counts[user_id] >= 4:  
        add_points(user_id, 1)  
        message_counts[user_id] = 0  
        # ربات چیزی نمی‌فرسته، فقط امتیاز میده  
  
# دستور روشن و خاموش کردن امتیازدهی پیام  
@bot.message_handler(commands=['offpm'])  
def disable_pm_award(message):  
    global pm_awarding_active  
    if not is_admin(message.from_user.id):  
        return  
    pm_awarding_active = False  
    bot.reply_to(message, "✅ سیستم امتیازدهی با پیام خاموش شد.")  
  
@bot.message_handler(commands=['onpm'])  
def enable_pm_award(message):  
    global pm_awarding_active  
    if not is_admin(message.from_user.id):  
        return  
    pm_awarding_active = True  
    bot.reply_to(message, "✅ سیستم امتیازدهی با پیام فعال شد.")  
  
# اجرای ربات  
bot.infinity_polling()
