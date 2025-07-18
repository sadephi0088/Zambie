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

conn = sqlite3.connect("data.db", checksamethread=False)
c = conn.cursor()

ایجاد جدول کاربران با ستون‌های کامل #
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
        partner_id INTEGER
    )
    ''')
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

pending_loves = {}

def add_user(message):
    userid = message.fromuser.id
    name = message.fromuser.firstname
    username = message.fromuser.username if message.fromuser.username else "ندارد"
    c.execute("SELECT userid FROM users WHERE userid = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (userid, name, username) VALUES (?, ?, ?)", (userid, name, username))
        conn.commit()

def getusername(userid):
    c.execute("SELECT username FROM users WHERE userid = ?", (userid,))
    data = c.fetchone()
    return data[0] if data else "ندارد ❌"

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
    userid = message.fromuser.id
    c.execute("SELECT * FROM users WHERE userid = ?", (userid,))
    data = c.fetchone()
    if data:
        tick = "دارد ✅" if data[5] == 1 or data[4] >= 5000 else "ندارد ❌"
        rank = get_rank(data[4])
        role = data[6] if data[6] else "ممبر عادی 🧍"
        birthdate = data[7] if data[7] else "ثبت نشده ❌"
        partner_id = data[8]
        partnerusername = getusername(partnerid) if partnerid else "ندارد ❌"

        text = f'''
━━━【 پروفایل شما در گروه 】━━━

•مشخصات فردی شما•
👤 نام: {data[1]}
✨ یوزرنیم: @{data[2]}
⚔️ آیدی عددی: {data[0]}

🌐 کشور شما: 🇮🇷 ایران

•• دارایی‌ها و امتیازت: ••
💰 سکه‌هات: {data[3]}
💎 امتیازت: {data[4]}
⚜️ نشان تایید طلایی: {tick}

•مشخصات خانواده شما•
😍 اسم همسر یا عشق‌ِت: {partner_username}
♥️ اسم فرزندتون:
🐣 حیوان خانگی شما:
♨️ فرقه‌ای که توش عضوی:

🌙 شکلک اختصاصی:
🎂 تاریخ تولدت: {birthdate}
🔮 قدرت‌ها و طلسم‌ها: (نحوه اجرا /shop)

:: در گروه :::::

▪︎🏆 درجه شما در گروه: {rank}
▪︎💠 مقام شما در گروه: {role}
'''
        bot.reply_to(message, text)

@bot.message_handler(commands=['old'])
def set_birthdate(message):
    userid = message.fromuser.id
    match = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', message.text.strip())
    if not match:
        bot.reply_to(message, "❌ فرمت تاریخ تولد اشتباه است. مثال:\n/old 1379/1/11")
        return
    birthdate = match.group(1)
    c.execute("SELECT coin FROM users WHERE userid = ?", (userid,))
    data = c.fetchone()
    if not data or data[0] < 40:
        bot.reply_to(message, "❌ سکه کافی برای ثبت تاریخ تولد نداری!")
        return
    c.execute("UPDATE users SET birthdate = ?, coin = coin - 40 WHERE userid = ?", (birthdate, userid))
    conn.commit()
    bot.reply_to(message, "🎂 تاریخ تولد ثبت شد و ۴۰ سکه کسر شد.")

@bot.message_handler(commands=['love'])
def love_request(message):
    if not message.replytomessage:
        bot.reply_to(message, "❌ ریپلای کن روی پیام کسی که می‌خوای عاشقش بشی.")
        return
    requesterid = message.fromuser.id
    target = message.replytomessage.from_user
    if requester_id == target.id:
        bot.reply_to(message, "❌ نمی‌تونی عاشق خودت بشی!")
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💖 قبول می‌کنم", callbackdata=f"accept{requester_id}"),
        types.InlineKeyboardButton("💔 قبول نمی‌کنم", callbackdata=f"reject{requester_id}")
    )
    text = f"💌 @{message.from_user.username} عاشق @{target.username} شده!\nآیا عشقش رو قبول می‌کنی؟ 😍"
    sent = bot.sendmessage(message.chat.id, text, replymarkup=markup)
    pendingloves[sent.messageid] = requester_id

@bot.callbackqueryhandler(func=lambda call: call.data.startswith("accept") or call.data.startswith("reject"))
def handleloveresponse(call):
    messageid = call.message.messageid
    if messageid not in pendingloves:
        bot.answercallbackquery(call.id, "❌ درخواست منقضی شده.")
        return
    requesterid = pendingloves[message_id]
    responderid = call.fromuser.id
    if call.data.startswith("accept_"):
        c.execute("SELECT coin FROM users WHERE userid = ?", (requesterid,))
        coin = c.fetchone()[0]
        if coin < 40:
            bot.editmessagetext("❌ درخواست‌کننده سکه کافی نداره!", call.message.chat.id, message_id)
            return
        c.execute("UPDATE users SET partnerid = ? WHERE userid = ?", (responderid, requesterid))
        c.execute("UPDATE users SET partnerid = ? WHERE userid = ?", (requesterid, responderid))
        c.execute("UPDATE users SET coin = coin - 40 WHERE userid = ?", (requesterid,))
        conn.commit()
        bot.editmessagetext("💖 عشق پذیرفته شد! تبریک به این زوج خوشبخت! 🎉", call.message.chat.id, message_id)
        bot.sendmessage(call.message.chat.id, f"🎊 @{getusername(requesterid)} و @{getusername(responder_id)} حالا عاشق هم هستن! 💘")
    else:
        bot.editmessagetext("💔 عشق رد شد. شاید یه روز دیگه... 😢", call.message.chat.id, message_id)
    del pendingloves[messageid]

@bot.message_handler(commands=['dlove'])
def divorce_love(message):
    userid = message.fromuser.id
@bot.message_handler(commands=['dlove'])
def divorce_love(message):
    userid = message.fromuser.id
    c.execute("SELECT partnerid FROM users WHERE userid = ?", (user_id,))
    data = c.fetchone()
    if not data or not data[0]:
        bot.reply_to(message, "❌ شما در رابطه‌ای نیستید.")
        return

    partner_id = data[0]
    c.execute("UPDATE users SET partnerid = NULL WHERE userid IN (?, ?)", (userid, partnerid))
    conn.commit()

    bot.sendmessage(message.chat.id, f"💔 رابطه بین @{getusername(userid)} و @{getusername(partner_id)} به پایان رسید... 😢\nگاهی عشق هم تموم میشه، ولی خاطره‌ها می‌مونن...")

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
    if message.replytomessage:
        userid = message.fromuser.id
        c.execute("SELECT coin FROM users WHERE userid = ?", (userid,))
        data = c.fetchone()
        if not data or data[0] < 20:
            bot.reply_to(message, "❌ سکه کافی برای اجرای طلسم بپاک نداری!")
            return
        try:
            bot.deletemessage(message.chat.id, message.replytomessage.messageid)
            c.execute("UPDATE users SET coin = coin - 20 WHERE userid = ?", (userid,))
            conn.commit()
            bot.reply_to(message, "🧼 پیام حذف شد و ۲۰ سکه از حساب شما کسر گردید.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا در حذف پیام: {str(e)}")
    else:
        bot.reply_to(message, "❌ برای اجرای دستور باید روی پیام ریپلای کنی.")

@bot.message_handler(commands=['mut'])
def mute_user(message):
    if message.replytomessage:
        userid = message.fromuser.id
        c.execute("SELECT coin FROM users WHERE userid = ?", (userid,))
        data = c.fetchone()
        if not data or data[0] < 80:
            bot.reply_to(message, "❌ سکه کافی برای اجرای طلسم حبس یخی نداری!")
            return
        try:
            bot.restrictchatmember(
                chat_id=message.chat.id,
                userid=message.replytomessage.fromuser.id,
                until_date=int(time.time()) + 60,
                cansendmessages=False
            )
            c.execute("UPDATE users SET coin = coin - 80 WHERE userid = ?", (userid,))
            conn.commit()
            bot.reply_to(message, "🧊 کاربر به مدت ۶۰ ثانیه سکوت شد و ۸۰ سکه از حساب شما کسر گردید.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا در اجرای طلسم حبس یخی: {str(e)}")
    else:
        bot.reply_to(message, "❌ برای اجرای دستور باید روی پیام کاربر مورد نظر ریپلای کنی.")

@bot.message_handler(commands=['tik'])
def give_tick(message):
    if message.replytomessage and message.fromuser.id == OWNERID:
        uid = message.replytomessage.from_user.id
        c.execute("UPDATE users SET goldtick = 1 WHERE userid = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "⚜️ نشان تایید طلایی برای این کاربر فعال شد ✅")

@bot.message_handler(commands=['dtik'])
def remove_tick(message):
    if message.replytomessage and message.fromuser.id == OWNERID:
        uid = message.replytomessage.from_user.id
        c.execute("UPDATE users SET goldtick = 0 WHERE userid = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "❌ نشان تایید طلایی از این کاربر برداشته شد.")

@bot.messagehandler(func=lambda m: m.replyto_message)
def control_points(message):
    if message.fromuser.id != OWNERID:
        return

    uid = message.replytomessage.from_user.id
    text = message.text.strip()

    if re.match(r'^\+ 🪙 \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET coin = coin + ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💰 {amount} سکه به حساب {uid} اضافه شد!")

    elif re.match(r'^\- 🪙 \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET coin = coin - ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💸 {amount} سکه از حساب {uid} کم شد!")

    elif re.match(r'^\+ \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"🎉 {amount} امتیاز اضافه شد!")

    elif re.match(r'^\- \d+$', text):
        amount = int(text.split()[-1])
        c.execute("UPDATE users SET score = score - ? WHERE user_id = ?", (amount, uid))
        conn.commit()
        bot.reply_to(message, f"💔 {amount} امتیاز کم شد!")

    elif re.match(r'^\+m\d{1,2}$', text):
        key = text[1:]
        if key in ranks:
            c.execute("UPDATE users SET role = ? WHERE user_id = ?", (ranks[key], uid))
            conn.commit()
            bot.reply_to(message, f"👑 مقام جدید: {ranks[key]} برای کاربر ثبت شد!")

    elif re.match(r'^\-m\d{1,2}$', text):
        c.execute("UPDATE users SET role = 'ممبر عادی 🧍' WHERE user_id = ?", (uid,))
        conn.commit()
        bot.reply_to(message, "🔻 مقام کاربر حذف شد و به حالت پیش‌فرض برگشت.")

bot.infinity_polling()
