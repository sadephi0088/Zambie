import telebot
from telebot import types
import sqlite3
import re
import time

TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
OWNER_ID = 7341748124
bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()
time.sleep(1)

conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

ساخت جدول کاربران با ستون‌های لازم

try:
c.execute('''
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
name TEXT,
username TEXT,
coin INTEGER DEFAULT 180,
score INTEGER DEFAULT 250,
gold_tick INTEGER DEFAULT 0,
role TEXT DEFAULT 'ممبر عادی 🧍',
birthdate TEXT,
partner TEXT,
child TEXT,
pet TEXT,
emoji TEXT,
blocked INTEGER DEFAULT 0
)
''')
conn.commit()
except Exception:
try:
c.execute("ALTER TABLE users ADD COLUMN birthdate TEXT")
c.execute("ALTER TABLE users ADD COLUMN partner TEXT")
c.execute("ALTER TABLE users ADD COLUMN child TEXT")
c.execute("ALTER TABLE users ADD COLUMN pet TEXT")
c.execute("ALTER TABLE users ADD COLUMN emoji TEXT")
c.execute("ALTER TABLE users ADD COLUMN blocked INTEGER DEFAULT 0")
conn.commit()
except:
pass

دیکشنری مقام‌ها

ranks = {
"m1": "سوگولی گروه 💋",
"m2": "پرنسس گروه 👑",
"m3": "ملکه گروه 👸",
"m4": "شوالیه گروه 🛡️",
"m5": "رهبر گروه 🦁",
"m6": "اونر گروه 🌀",
"m7": "زامبی الفا گروه 🧟‍♂️",
"m8": "نفس گروه 💨",
"m9": "بادیگارد گروه 🕶️",
"m10": "ممبر عادی 🧍",
"m11": "عاشق دلباخته ❤️‍🔥",
"m12": "برده گروه 🧎",
"m13": "رئیس گروه 🧠",
"m14": "کصشرگوی گروه 🐵",
"m15": "دختر شاه 👑👧"
}

admins = set()
message_count = {}
counting_active = {}

def add_user(message):
user_id = message.from_user.id
name = message.from_user.first_name
username = message.from_user.username if message.from_user.username else "ندارد"

c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))  
if not c.fetchone():  
    c.execute("INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)", (user_id, name, username))  
    conn.commit()

def get_rank(score):
if score < 500:
return "تازه‌کار 👶"
elif score < 1000:
return "حرفه‌ای 🔥"
elif score < 2000:
return "استاد 🌟"
elif score < 4000:
return "قهرمان 🏆"
elif score < 7000:
return "افسانه‌ای 🐉"
elif score < 10000:
return "بی‌نظیر 💎"
else:
return "اسطوره 🚀"

def user_blocked(user_id):
c.execute("SELECT blocked FROM users WHERE user_id = ?", (user_id,))
res = c.fetchone()
if res and res[0] == 1:
return True
return False

@bot.message_handler(commands=['my'])
def show_profile(message):
add_user(message)
user_id = message.from_user.id
if user_blocked(user_id):
bot.reply_to(message, "❌ عزیزم، تو در حالت تعلیق هستی و نمی‌تونی از این امکانات استفاده کنی.")
return
c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
data = c.fetchone()
if data:
tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"
rank = get_rank(data[4])
role = data[6] if data[6] else "ممبر عادی 🧍"
birthdate = data[7] if data[7] else ""
partner = data[8] if data[8] else ""
child = data[9] if data[9] else ""
pet = data[10] if data[10] else ""
emoji = data[11] if data[11] else ""

text = f'''

━━━【 پروفایل زیبات ♥️ 】━━━

👤 نام: {data[1]}
✨ یوزرنیم: @{data[2]}
⚔️ آیدی عددی: {data[0]}

🌐 کشور تو ایران 🇮🇷 عزیزم

•• دارایی‌ها و امتیازت: ••
💰 سکه‌هات: {data[3]}
💎 امتیازت: {data[4]}
⚜️ نشان طلایی: {tick}

•مشخصات خانواده و عشقت•
😍 عشق من: {partner if partner else "ندارد"}
♥️ فرزند دلبر: {child if child else "ندارد"}
🐣 حیوان خانگی دوست‌داشتنی: {pet if pet else "ندارد"}

🌙 شکلک اختصاصی: {emoji if emoji else "ندارد"}
🎂 تاریخ تولدت: {birthdate if birthdate else "ثبت نشده"}

🔮 قدرت‌ها و طلسم‌ها: (دستور /shop)

:: در گروه ::

🏆 رتبه تو: {rank}
💠 مقام تو: {role}
'''
bot.reply_to(message, text)

@bot.message_handler(commands=['old'])
def set_birthdate(message):
user_id = message.from_user.id
text = message.text.strip()

if user_blocked(user_id):  
    bot.reply_to(message, "❌ عزیزم، حساب تو در حالت تعلیقه و نمیتونی تاریخ تولد ثبت کنی.")  
    return  

match = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', text)  
if not match:  
    bot.reply_to(message, "❌ فرمت تاریخ تولد اشتباهه، مثل این بفرست:\n/old 1379/1/11")  
    return  

birthdate = match.group(1)  

c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))  
data = c.fetchone()  
if not data or data[0] < 40:  
    bot.reply_to(message, "❌ عزیزم سکه کافی برای ثبت تاریخ تولد نداری، ۴۰ سکه لازمه.")  
    return  

c.execute("UPDATE users SET birthdate = ?, coin = coin - 40 WHERE user_id = ?", (birthdate, user_id))  
conn.commit()  
bot.reply_to(message, f"🎂 تولدت ثبت شد و ۴۰ سکه از حسابت کسر گردید، عزیزم مبارکه! 💖")

@bot.message_handler(commands=['partner'])
def set_partner(message):
user_id = message.from_user.id
if user_blocked(user_id):
bot.reply_to(message, "❌ عزیزم، در حالت تعلیق هستی و نمی‌تونی عشقت رو ثبت کنی.")
return
text = message.text.strip()
parts = text.split(' ', 1)
if len(parts) < 2 or not parts[1].strip():
bot.reply_to(message, "❌ عزیزم، برای ثبت عشق از این دستور استفاده کن:\n/partner اسم_عشق_تو\nهزینه 50 سکه است.")
return
partner_name = parts[1].strip()

c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))  
data = c.fetchone()  
if not data or data[0] < 50:  
    bot.reply_to(message, "❌ سکه کافی برای ثبت عشق نداری، ۵۰ سکه لازمه.")  
    return  

c.execute("UPDATE users SET partner = ?, coin = coin - 50 WHERE user_id = ?", (partner_name, user_id))  
conn.commit()  
bot.reply_to(message, f"😍 عشق زیبات ثبت شد: {partner_name} و ۵۰ سکه از حسابت کم شد. عاشقانه‌ام!")

@bot.message_handler(commands=['child'])
def set_child(message):
user_id = message.from_user.id
if user_blocked(user_id):
bot.reply_to(message, "❌ عزیزم، در حالت تعلیق هستی و نمی‌تونی فرزندت رو ثبت کنی.")
return
text = message.text.strip()
parts = text.split(' ', 1)
if len(parts) < 2 or not parts[1].strip():
bot.reply_to(message, "❌ عزیزم، برای ثبت فرزند از این دستور استفاده کن:\n/child اسم_فرزند\nهزینه 40 سکه است.")
return
child_name = parts[1].strip()

c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))  
data = c.fetchone()  
if not data or data[0] < 40:  
    bot.reply_to(message, "❌ سکه کافی برای ثبت فرزند نداری، ۴۰ سکه لازمه.")  
    return  

c.execute("UPDATE users SET child = ?, coin = coin - 40 WHERE user_id = ?", (child_name, user_id))  
conn.commit()  
bot.reply_to(message, f"♥️ فرزندت ثبت شد: {child_name} و ۴۰ سکه از حسابت کم شد. عاشقانه و شیرین!")

@bot.message_handler(commands=['pet'])
def set_pet(message):
user_id = message.from_user.id
if user_blocked(user_id):
bot.reply_to(message, "❌ عزیزم، در حالت تعلیق هستی و نمی‌تونی حیوان خانگی ثبت کنی.")
return
text = message.text.strip()
parts = text.split(' ', 1)
if len(parts) < 2 or not parts[1].strip():
bot.reply_to(message, "❌ عزیزم، برای ثبت حیوان خانگی از این دستور استفاده کن:\n/pet اسم_حیوان\nهزینه 30 سکه است.")
return
pet_name = parts[1].strip()

c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))  
data = c.fetchone()  
if not data or data[0] < 30:  
    bot.reply_to(message, "❌ سکه کافی برای ثبت حیوان خانگی نداری، ۳۰ سکه لازمه.")  
    return  

c.execute("UPDATE users SET pet = ?, coin = coin - 30 WHERE user_id = ?", (pet_name, user_id))  
conn.commit()  
bot.reply_to(message, f"🐣 حیوان خانگی دوست‌داشتنی‌ت ثبت شد: {pet_name} و ۳۰ سکه از حسابت کم شد. دلبرانه!")

@bot.message_handler(commands=['emoji'])
def set_emoji(message):
user_id = message.from_user.id
if user_blocked(user_id):
bot.reply_to(message, "❌ عزیزم، در حالت تعلیق هستی و نمی‌تونی شکلک اختصاصی ثبت کنی.")
return
text = message.text.strip()
parts = text.split(' ', 1)
if len(parts) < 2 or not parts[1].strip():
bot.reply_to(message, "❌ عزیزم، برای ثبت شکلک اختصاصی از این دستور استفاده کن:\n/emoji شکلک\nهزینه 20 سکه است.")
return
emoji = parts[1].strip()

c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))  
data = c.fetchone()  
if not data or data[0] < 20:  
    bot.reply_to(message, "❌ سکه کافی برای ثبت شکلک اختصاصی نداری، ۲۰ سکه لازمه.")  
    return  

c.execute("UPDATE users SET emoji = ?, coin = coin - 20 WHERE user_id = ?", (emoji, user_id))  
conn.commit()  
bot.reply_to(message, f"🌙 شکلک اختصاصی‌ت ثبت شد: {emoji} و ۲۰ سکه از حسابت کم شد. عشقم! 💖")

@bot.message_handler(commands=['give'])
def give_coins(message):
user_id = message.from_user.id
if user_blocked(user_id):
bot.reply_to(message, "❌ تو در حالت تعلیق هستی و نمی‌تونی سکه منتقل کنی.")
return
text = message.text.strip()
parts = text.split(' ')
if len(parts) != 3 or not parts[2].isdigit():
bot.reply_to(message, "❌ دستور اشتباهه. به شکل زیر وارد کن:\n/give @username تعداد_سکه")
return
username = parts[1].lstrip('@')
amount = int(parts[2])

if amount <= 0:  
    bot.reply_to(message, "❌ تعداد سکه باید بیشتر از صفر باشه.")  
    return  

c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))  
data = c.fetchone()  
if not data or data[0] < amount:  
    bot.reply_to(message, "❌ سکه کافی نداری برای انتقال.")  
    return  

c.execute("SELECT user_id FROM users WHERE username = ?", (username,))  
res = c.fetchone()  
if not res:  
    bot.reply_to(message, "❌ کاربری با این یوزرنیم پیدا نشد.")  
    return  

receiver_id = res[0]  
if receiver_id == user_id:  
    bot.reply_to(message, "❌ نمی‌تونی به خودت سکه بدی، عزیزم!")  
    return  

c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (amount, user_id))  
c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amount, receiver_id))  
conn.commit()  

bot.reply_to(message, f"💖 {amount} سکه عاشقانه به @{username} منتقل شد، دلبرم!")

ادمین‌ها: افزودن، حذف، ریست توسط مالک

@bot.message_handler(commands=['admin'])
def add_admin(message):
if message.from_user.id != OWNER_ID:
return
if not message.reply_to_message:
bot.reply_to(message, "❌ برای افزودن ادمین، روی پیام کاربر ریپلای کن.")
return
uid = message.reply_to_message.from_user.id
admins.add(uid)
bot.reply_to(message, f"👑 کاربر {uid} به جمع ادمین‌های عزیز اضافه شد!")

@bot.message_handler(commands=['dadmin'])
def del_admin(message):
if message.from_user.id != OWNER_ID:
return
if not message.reply_to_message:
bot.reply_to(message, "❌ برای حذف ادمین، روی پیام کاربر ریپلای کن.")
return
uid = message.reply_to_message.from_user.id
if uid in admins:
admins.remove(uid)
bot.reply_to(message, f"❌ کاربر {uid} از ادمین‌ها حذف شد.")
else:
bot.reply_to(message, "❌ این کاربر ادمین نیست.")

@bot.message_handler(commands=['ddadmin'])
def reset_admins(message):
if message.from_user.id != OWNER_ID:
return
admins.clear()
bot.reply_to(message, "🔄 همه ادمین‌ها پاکسازی شدند و فقط مالک عزیز باقی ماند.")

تعلیق کاربر

@bot.message_handler(commands=['block'])
def block_user(message):
if message.from_user.id not in admins and message.from_user.id != OWNER_ID:
return
if not message.reply_to_message:
bot.reply_to(message, "❌ برای تعلیق، روی پیام کاربر ریپلای کن.")
return
uid = message.reply_to_message.from_user.id
c.execute("UPDATE users SET blocked = 1 WHERE user_id = ?", (uid,))
conn.commit()
bot.reply_to(message, f"⛔️ کاربر {uid} عزیز، به حالت تعلیق درآمدی. 😔")

@bot.message_handler(commands=['unblock'])
def unblock_user(message):
if message.from_user.id not in admins and message.from_user.id != OWNER_ID:
return
if not message.reply_to_message:
bot.reply_to(message, "❌ برای رفع تعلیق، روی پیام کاربر ریپلای کن.")
return
uid = message.reply_to_message.from_user.id
c.execute("UPDATE users SET blocked = 0 WHERE user_id = ?", (uid,))
conn.commit()
bot.reply_to(message, f"💖 کاربر {uid} عزیز، تعلیق برداشته شد و خوش‌آمدی!")

شمارشگر پیام گروه با جایزه سکه و امتیاز

@bot.message_handler(commands=['on'])
def start_counting(message):
chat_id = message.chat.id
if message.from_user.id not in admins and message.from_user.id != OWNER_ID:
return
counting_active[chat_id] = True
message_count[chat_id] = {}
bot.reply_to(message, "🎉 شمارش پیام‌ها فعال شد! هر ۵۰ پیام، هدیه عاشقانه برنده می‌شی عزیزم!")

@bot.message_handler(commands=['off'])
def stop_counting(message):
chat_id = message.chat.id
if message.from_user.id not in admins and message.from_user.id != OWNER_ID:
return
if chat_id in counting_active:
counting_active[chat_id] = False
bot.reply_to(message, "🔕 شمارش پیام‌ها متوقف شد، هر وقت خواستی دوباره روشن کن! 💖")

@bot.message_handler(func=lambda m: True)
def count_messages(message):
chat_id = message.chat.id
user_id = message.from_user.id
if user_blocked(user_id):
return
if chat_id not in counting_active or not counting_active.get(chat_id, False):
return
if user_id not in message_count.get(chat_id, {}):
message_count[chat_id][user_id] = 0
message_count[chat_id][user_id] += 1

if message_count[chat_id][user_id] % 50 == 0:  
    # جایزه دادن  
    c.execute("SELECT coin, score FROM users WHERE user_id = ?", (user_id,))  
    data = c.fetchone()  
    if data:  
        new_coin = data[0] + 100  # جایزه ۱۰۰ سکه  
        new_score = data[1] + 50  # جایزه ۵۰ امتیاز  
        c.execute("UPDATE users SET coin = ?, score = ? WHERE user_id = ?", (new_coin, new_score, user_id))  
        conn.commit()  
        bot.send_message(chat_id, f"🎉 تبریک {message.from_user.first_name} عزیز! تو به {message_count[chat_id][user_id]} پیام رسیدی و ۱۰۰ سکه و ۵۰ امتیاز هدیه گرفتی! 💖✨")

دستور /shop با توضیحات زیبا و عاشقانه

@bot.message_handler(commands=['shop'])
def show_shop(message):
text = '''
✨ فروشگاه قدرت‌ها و طلسم‌های جادویی ✨

1️⃣ 🧼 طلسم بپاک
• دستور: ریپلای روی پیام + /del
• هزینه: ۲۰ سکه
• توضیح: پیام ریپلای شده را به سرعت و بی‌صدا پاک کن!

2️⃣ 🧊 طلسم حبس یخی
• دستور: ریپلای روی کاربر + /mut
• هزینه: ۸۰ سکه
• توضیح: کاربر مورد نظر را ۶۰ ثانیه در سکوت کامل فرو ببر!

💖 برای استفاده، روی پیام فرد مورد نظر ریپلای کرده و دستور را بفرست.

دل عاشقت همراهت 💝
'''
bot.reply_to(message, text)

دستور /del برای پاک کردن پیام با هزینه و متن زیبا

@bot.message_handler(commands=['del'])
def delete_message(message):
if message.reply_to_message:
user_id = message.from_user.id
c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
data = c.fetchone()
if not data or data[0] < 20:
bot.reply_to(message, "❌ عزیزم، سکه کافی نداری برای اجرای طلسم بپاک! فقط ۲۰ سکه لازمه.")
return
try:
bot.delete_message(message.chat.id, message.reply_to_message.message_id)
c.execute("UPDATE users SET coin = coin - 20 WHERE user_id = ?", (user_id,))
conn.commit()
bot.reply_to(message, "🧼 پیام پاک شد و ۲۰ سکه از حسابت کسر گردید. عاشقتم! 💖")
except Exception as e:
bot.reply_to(message, f"❌ اوه! مشکلی پیش اومد در حذف پیام: {str(e)}")
else:
bot.reply_to(message, "❌ باید روی پیام مورد نظر ریپلای کنی تا پاکش کنم.")

دستور /mut برای سکوت دادن کاربر با هزینه و متن عاشقانه

@bot.message_handler(commands=['mut'])
def mute_user(message):
if message.reply_to_message:
user_id = message.from_user.id
c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
data = c.fetchone()
if not data or data[0] < 80:
bot.reply_to(message, "❌ عزیزم، سکه کافی نداری برای اجرای طلسم حبس یخی! ۸۰ سکه لازمه.")
return
try:
bot.restrict_chat_member(
chat_id=message.chat.id,
user_id=message.reply_to_message.from_user.id,
until_date=int(time.time()) + 60,
can_send_messages=False
)
c.execute("UPDATE users SET coin = coin - 80 WHERE user_id = ?", (user_id,))
conn.commit()
bot.reply_to(message, "🧊 کاربر به مدت ۶۰ ثانیه سکوت شد و ۸۰ سکه از حسابت کم گردید. با عشق!")
except Exception as e:
bot.reply_to(message, f"❌ مشکلی در اجرای طلسم حبس یخی پیش اومد: {str(e)}")
else:
bot.reply_to(message, "❌ باید روی پیام کاربر مورد نظر ریپلای کنی تا سکوتش کنم.")

دستور /tik و /dtik فقط برای مالک، برای دادن یا گرفتن نشان طلایی

@bot.message_handler(commands=['tik'])
def give_tick(message):
if message.reply_to_message and message.from_user.id == OWNER_ID:
uid = message.reply_to_message.from_user.id
c.execute("UPDATE users SET gold_tick = 1 WHERE user_id = ?", (uid,))
conn.commit()
bot.reply_to(message, "⚜️ نشان تایید طلایی با عشق به این عزیز داده شد. مبارک باشه! ✅")

@bot.message_handler(commands=['dtik'])
def remove_tick(message):
if message.reply_to_message and message.from_user.id == OWNER_ID:
uid = message.reply_to_message.from_user.id
c.execute("UPDATE users SET gold_tick = 0 WHERE user_id = ?", (uid,))
conn.commit()
bot.reply_to(message, "❌ نشان طلایی به احترام برداشته شد.")

دستوراتی برای تغییر سکه، امتیاز، مقام توسط مالک با متن زیبا

@bot.message_handler(func=lambda m: m.reply_to_message and m.from_user.id == OWNER_ID)
def control_points(message):
uid = message.reply_to_message.from_user.id
text = message.text.strip()

# اضافه کردن سکه  
if re.match(r'^\+ 🪙 \d+$', text):  
    amount = int(text.split()[-1])  
    c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amount, uid))  
    conn.commit()  
    bot.reply_to(message, f"💰 {amount} سکه با عشق به حساب عزیز {uid} اضافه شد! 💝")  

# کم کردن سکه  
elif re.match(r'^\- 🪙 \d+$', text):  
    amount = int(text.split()[-1])  
    c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (amount, uid))  
    conn.commit()  
    bot.reply_to(message, f"💸 {amount} سکه از حساب عزیز {uid} کم شد! دلتنگتم!")  

# اضافه کردن امتیاز  
elif re.match(r'^\+ \d+$', text):  
    amount = int(text.split()[-1])  
    c.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (amount, uid))  
    conn.commit()  
    bot.reply_to(message, f"🎉 {amount} امتیاز به عزیز {uid} اضافه شد! افتخار می‌کنم!")  

# کم کردن امتیاز  
elif re.match(r'^\- \d+$', text):  
    amount = int(text.split()[-1])  
    c.execute("UPDATE users SET score = score - ? WHERE user_id = ?", (amount, uid))  
    conn.commit()  
    bot.reply_to(message, f"💔 {amount} امتیاز از عزیز {uid} کم شد! نگرانم!")  

# افزودن مقام  
elif re.match(r'^\+m\d{1,2}$', text):  
    key = text[1:]  
    if key in ranks:  
        c.execute("UPDATE users SET role = ? WHERE user_id = ?", (ranks[key], uid))  
        conn.commit()  
        bot.reply_to(message, f"👑 مقام عاشقانه {ranks[key]} با افتخار به کاربر عزیز داده شد!")  

# حذف مقام (بازگشت به ممبر عادی)  
elif re.match(r'^\-m\d{1,2}$', text):  
    c.execute("UPDATE users SET role = 'ممبر عادی 🧍' WHERE user_id = ?", (uid,))  
    conn.commit()  
    bot.reply_to(message, "🔻 مقام عزیز به حالت پیش‌فرض برگشت.")

bot.infinity_polling()

