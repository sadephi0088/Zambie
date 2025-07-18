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

ایجاد جدول users و اضافه کردن ستون‌ها در صورت نیاز

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
love TEXT DEFAULT '-',
love_id INTEGER DEFAULT 0,
pending_love TEXT DEFAULT '-'
)
''')
conn.commit()
except Exception:

اگر جدول قبلاً بوده و ستون‌های جدید نبودند، اضافه کن

try:
c.execute("ALTER TABLE users ADD COLUMN birthdate TEXT")
c.execute("ALTER TABLE users ADD COLUMN love TEXT DEFAULT '-'")
c.execute("ALTER TABLE users ADD COLUMN love_id INTEGER DEFAULT 0")
c.execute("ALTER TABLE users ADD COLUMN pending_love TEXT DEFAULT '-'")
conn.commit()
except:
pass  # ستون‌ها قبلا وجود دارند، رد می‌کنیم

دیکشنری مقام‌ها با ایموجی

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

@bot.message_handler(commands=['my'])
def show_profile(message):
add_user(message)
user_id = message.from_user.id
c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
data = c.fetchone()
if data:
tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"
rank = get_rank(data[4])
role = data[6] if data[6] else "ممبر عادی 🧍"
birthdate = data[7] if len(data) > 7 and data[7] else "ثبت نشده ❌"
love_name = data[8] if len(data) > 8 and data[8] != '-' else "ندارد ❌"
love_id = data[9] if len(data) > 9 else 0
love_username = "-"
if love_id and love_id != 0:
try:
user = bot.get_chat_member(message.chat.id, love_id)
love_username = user.user.username if user.user.username else "ندارد"
except:
love_username = "ندارد"
else:
love_username = "ندارد"

text = f'''

━━━【 پروفایل شما در گروه 】━━━

• مشخصات فردی شما •
👤 نام: {data[1]}
✨ یوزرنیم: @{data[2]}
⚔️ آیدی عددی: {data[0]}

🌐 کشور شما: 🇮🇷 ایران

•• دارایی‌ها و امتیازات ••
💰 سکه‌ها: {data[3]}
💎 امتیاز: {data[4]}
⚜️ نشان تایید طلایی: {tick}

• مشخصات خانواده شما •
😍 اسم همسر یا عشق‌ِت: {love_name}
✨ یوزرنیم همسر: @{love_username}
♥️ اسم فرزندتون:
🐣 حیوان خانگی شما:
♨️ فرقه‌ای که توش عضوی:

🌙 شکلک اختصاصی:
🎂 تاریخ تولد: {birthdate}
🔮 قدرت‌ها و طلسم‌ها: (نحوه اجرا /shop)

:: در گروه ::

▪︎🏆 درجه شما در گروه: {rank}
▪︎💠 مقام شما در گروه: {role}
'''
bot.reply_to(message, text)

@bot.message_handler(commands=['old'])
def set_birthdate(message):
user_id = message.from_user.id
text = message.text.strip()

match = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', text)
if not match:
bot.reply_to(message, "❌ فرمت تاریخ تولد اشتباه است. لطفاً به شکل زیر وارد کنید:\n/old 1379/1/11")
return

birthdate = match.group(1)

c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
data = c.fetchone()
if not data or data[0] < 40:
bot.reply_to(message, "❌ سکه کافی برای ثبت تاریخ تولد نداری!")
return

c.execute("UPDATE users SET birthdate = ?, coin = coin - 40 WHERE user_id = ?", (birthdate, user_id))
conn.commit()
bot.reply_to(message, f"🎂 تاریخ تولد شما در پروفایلت ثبت شد و ۴۰ سکه از حسابت کسر گردید. 🎉")

@bot.message_handler(commands=['tik'])
def give_tick(message):
if message.reply_to_message and message.from_user.id == OWNER_ID:
uid = message.reply_to_message.from_user.id
c.execute("UPDATE users SET gold_tick = 1 WHERE user_id = ?", (uid,))
conn.commit()
bot.reply_to(message, "⚜️ نشان تایید طلایی برای این کاربر فعال شد ✅")

@bot.message_handler(commands=['dtik'])
def remove_tick(message):
if message.reply_to_message and message.from_user.id == OWNER_ID:
uid = message.reply_to_message.from_user.id
c.execute("UPDATE users SET gold_tick = 0 WHERE user_id = ?", (uid,))
conn.commit()
bot.reply_to(message, "❌ نشان تایید طلایی از این کاربر برداشته شد.")

@bot.message_handler(commands=['shop'])
def show_shop(message):
text = '''
🎁 قدرت‌ها و طلسم‌های فعالت:

1️⃣ 🧼 طلسم بپاک
• دستور استفاده: ریپلای روی پیام + /del
• هزینه: ۲۰ سکه
• توضیح: پیام ریپلای‌شده را پاک می‌کنی، بی‌صدا و سریع!

2️⃣ 🧊 طلسم حبس یخی
• دستور استفاده: ریپلای روی کاربر + /mut
• هزینه: ۸۰ سکه
• توضیح: کاربر را برای ۶۰ ثانیه به حالت سکوت می‌بری!
'''
bot.reply_to(message, text)

@bot.message_handler(commands=['del'])
def delete_message(message):
if message.reply_to_message:
user_id = message.from_user.id
c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
data = c.fetchone()
if not data or data[0] < 20:
bot.reply_to(message, "❌ سکه کافی برای اجرای طلسم بپاک نداری!")
return
try:
bot.delete_message(message.chat.id, message.reply_to_message.message_id)
c.execute("UPDATE users SET coin = coin - 20 WHERE user_id = ?", (user_id,))
conn.commit()
bot.reply_to(message, "🧼 پیام حذف شد و ۲۰ سکه از حساب شما کسر گردید.")
except Exception as e:
bot.reply_to(message, f"❌ خطا در حذف پیام: {str(e)}")
else:
bot.reply_to(message, "❌ برای اجرای دستور باید روی پیام ریپلای کنی.")

@bot.message_handler(commands=['mut'])
def mute_user(message):
if message.reply_to_message:
user_id = message.from_user.id
c.execute("SELECT coin FROM users WHERE user_id = ?", (user_id,))
data = c.fetchone()
if not data or data[0] < 80:
bot.reply_to(message, "❌ سکه کافی برای اجرای طلسم حبس یخی نداری!")
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
bot.reply_to(message, "🧊 کاربر به مدت ۶۰ ثانیه سکوت شد و ۸۰ سکه از حساب شما کسر گردید.")
except Exception as e:
bot.reply_to(message, f"❌ خطا در اجرای طلسم حبس یخی: {str(e)}")
else:
bot.reply_to(message, "❌ برای اجرای دستور باید روی پیام کاربر مورد نظر ریپلای کنی.")

@bot.message_handler(func=lambda m: m.reply_to_message)
def control_points(message):
if message.from_user.id != OWNER_ID:
return

uid = message.reply_to_message.from_user.id
text = message.text.strip()

سکه

if re.match(r'^+ 🪙 \d+$', text):
amount = int(text.split()[-1])
c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amount, uid))
conn.commit()
bot.reply_to(message, f"💰 {amount} سکه به حساب {uid} اضافه شد!", parse_mode="HTML")

elif re.match(r'^- 🪙 \d+$', text):
amount = int(text.split()[-1])
c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (amount, uid))
conn.commit()
bot.reply_to(message, f"💸 {amount} سکه از حساب {uid} کم شد!", parse_mode="HTML")

امتیاز

elif re.match(r'^+ \d+$', text):
amount = int(text.split()[-1])
c.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (amount, uid))
conn.commit()
bot.reply_to(message, f"🎉 {amount} امتیاز اضافه شد!", parse_mode="HTML")

elif re.match(r'^- \d+$', text):
amount = int(text.split()[-1])
c.execute("UPDATE users SET score = score - ? WHERE user_id = ?", (amount, uid))
conn.commit()
bot.reply_to(message, f"💔 {amount} امتیاز کم شد!", parse_mode="HTML")

مقام اضافه کردن

elif re.match(r'^+m\d{1,2}$', text):
key = text[1:]
if key in ranks:
c.execute("UPDATE users SET role = ? WHERE user_id = ?", (ranks[key], uid))
conn.commit()
bot.reply_to(message, f"👑 مقام جدید: <b>{ranks[key]}</b> برای کاربر ثبت شد!", parse_mode="HTML")

مقام حذف کردن

elif re.match(r'^-m\d{1,2}$', text):
c.execute("UPDATE users SET role = 'ممبر عادی 🧍' WHERE user_id = ?", (uid,))
conn.commit()
bot.reply_to(message, "🔻 مقام کاربر حذف شد و به حالت پیش‌فرض برگشت.")

-------------------- بخش ازدواج و طلاق --------------------

pending_requests = {}  # نگهداری درخواست‌های ازدواج: کلید = درخواست‌کننده, مقدار = id درخواست‌شده

@bot.message_handler(commands=['love'])
def love_request(message):
user_id = message.from_user.id
if not message.reply_to_message:
bot.reply_to(message, "برای ازدواج باید به پیام کسی ریپلای کنی 😍")
return

lover_id = message.reply_to_message.from_user.id

if lover_id == user_id:
bot.reply_to(message, "با خودت که نمی‌تونی ازدواج کنی عزیزم 😅")
return

add_user(message)  # ثبت درخواست‌کننده اگر نیست

چک کن درخواست فعالی هست یا نه

if user_id in pending_requests:
bot.reply_to(message, "❌ تو قبلاً یک درخواست ازدواج فرستادی که هنوز جواب داده نشده!")
return

چک کن که خود شخص هدف هم فرم داره

c.execute("SELECT user_id FROM users WHERE user_id = ?", (lover_id,))
if not c.fetchone():
bot.reply_to(message, "طرف مقابل هنوز فرم نداره، بگو اول یه پیام بده ✨")
return

چک سکه درخواست‌کننده

c.execute("SELECT coin, love, pending_love FROM users WHERE user_id = ?", (user_id,))
data = c.fetchone()
if not data:
bot.reply_to(message, "اول با یه پیام دیگه فرم بساز بعد دوباره تلاش کن 🌸")
return
coin, love, pending_love = data
if coin < 40:
bot.reply_to(message, "برای ازدواج باید ۴۰ سکه داشته باشی 💰")
return

if love != '-' and love != '':
bot.reply_to(message, "تو قبلاً ازدواج کردی عزیزم 💞")
return

if pending_love != '-' and pending_love != '':
bot.reply_to(message, "❌ تو در حال حاضر یک درخواست ازدواج داری که هنوز جواب ندادی!")
return

ثبت درخواست

pending_requests[user_id] = lover_id
c.execute("UPDATE users SET pending_love = ? WHERE user_id = ?", (str(lover_id), user_id))
conn.commit()

bot.reply_to(message, f"✅ درخواست ازدواج به کاربر ارسال شد. {message.reply_to_message.from_user.first_name} عزیز، برای قبول درخواست، به این پیام ریپلای کن و دستور /accept را بفرست.")

@bot.message_handler(commands=['accept'])
def accept_love(message):
user_id = message.from_user.id

باید ریپلای باشه روی پیام درخواست ازدواج

if not message.reply_to_message:
bot.reply_to(message, "برای قبول درخواست ازدواج باید روی پیام درخواست ازدواج ریپلای کنی.")
return

صاحب درخواست (ارسال کننده)

replied_user_id = message.reply_to_message.from_user.id

بررسی درخواست

if replied_user_id not in pending_requests:
bot.reply_to(message, "درخواست ازدواج معتبر پیدا نشد.")
return

if pending_requests[replied_user_id] != user_id:
bot.reply_to(message, "این درخواست ازدواج به تو ارسال نشده است.")
return

چک سکه درخواست‌کننده مجدد (برای اطمینان)

c.execute("SELECT coin FROM users WHERE user_id = ?", (replied_user_id,))
coin_data = c.fetchone()

if not coin_data or coin_data[0] < 40:
bot.reply_to(message, "کسی که درخواست ازدواج داده سکه کافی ندارد.")
return

ثبت عشق و عشق آیدی دوطرف

c.execute("SELECT name FROM users WHERE user_id = ?", (replied_user_id,))
lover_name = c.fetchone()[0]

c.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
user_name = c.fetchone()[0]

ثبت ازدواج در دیتابیس

c.execute("UPDATE users SET love = ?, love_id = ?, pending_love = '-' WHERE user_id = ?", (user_name, user_id, replied_user_id))
c.execute("UPDATE users SET love = ?, love_id = ?, pending_love = '-' WHERE user_id = ?", (lover_name, replied_user_id, user_id))

کم کردن 40 سکه از درخواست کننده

c.execute("UPDATE users SET coin = coin - 40 WHERE user_id = ?", (replied_user_id,))
conn.commit()

del pending_requests[replied_user_id]

ارسال پیام عاشقانه و شادی در گروه

bot.send_message(message.chat.id, f"💖🎉 {lover_name} و {user_name} حالا رسماً با هم ازدواج کردند! تبریک میگم به این زوج خوشبخت! 💍❤️")

@bot.message_handler(commands=['divorce'])
def divorce(message):
user_id = message.from_user.id

c.execute("SELECT love, love_id FROM users WHERE user_id = ?", (user_id,))
data = c.fetchone()
if not data:
bot.reply_to(message, "❌ اول باید ثبت نام کنی عزیزم!")
return

love_name = data[0]
love_id = data[1]

if love_name == '-' or love_id == 0:
bot.reply_to(message, "❌ تو الان ازدواج نکردی که طلاق بگیری!")
return

پاک کردن ازدواج برای هر دو طرف

c.execute("UPDATE users SET love = '-', love_id = 0 WHERE user_id = ?", (user_id,))
c.execute("UPDATE users SET love = '-', love_id = 0 WHERE user_id = ?", (love_id,))
conn.commit()

bot.reply_to(message, "💔 طلاق ثبت شد. حالا هر دو آزاد هستید!")

پیام به گروه در مورد طلاق

bot.send_message(message.chat.id, f"💔 {message.from_user.first_name} و {love_name} از هم طلاق گرفتند. برای هر دویشان آرزوی خوشبختی داریم!")

پاک کردن درخواست‌های در حال انتظار اگر باشند

if user_id in pending_requests:
del pending_requests[user_id]
if love_id in pending_requests:
del pending_requests[love_id]

اجرای ربات

bot.infinity_polling()

