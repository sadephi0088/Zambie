import telebot
import time
import random

TOKEN = '8049022187:AAEoR_IorwWZ8KaH_UMvCo2fa1LjTqhnlWY'
OWNER_ID = 7341748124
ADMINS = {OWNER_ID}
ENEMIES = set()

bot = telebot.TeleBot(TOKEN)

# متن پنل راهنما
help_text = """⚔️ 《 راهنمای ربات محافظتی - نسخه 1.0 》 ⚔️
——————————————————————
🛡️ دستورات اصلی: [محافظت از شما]🩸
1️⃣ /d  ارسال به گروه "جمله شما"
2️⃣ /spam "متن شما" "عدد"
3️⃣ /doshman "نابود کردن دشمنان"
4️⃣ /mutee "سکوت کاربر-دشمن"
5️⃣ /sik "حذف کاربر از گروه" 
——————————————————————
⚔️ دستورات واکنش به کاربران:👤
6️⃣ /idd "در آوردن اطلاعات فرد" 
7️⃣ /m "معرفی ربات محافظتی به کاربر"  
8️⃣ /tagg "صدا زدن تمامی افراد گروه"
——————————————————————
🔒 دستورات مدیریت گروه:👨‍💻
9️⃣ /zedlink "فعالسازی قفل لینک"  
🔟 /pinn "پین کردن پیام"
1️⃣1️⃣ /ghofle "قفل کامل گروه"
——————————————————————
🏷️ سایر دستورات:👾
1️⃣2️⃣ /adminn "افزودن مدیر ربات"
1️⃣3️⃣ /bgo "حرف‌زدن با من"
——————————————————————
⚠️ توجه:  
تمام دستورات فقط توسط مالک و مدیران ربات قابل اجراست.  
برای لغو دستورات، ابتدای همان دستور بنویسید "d" [مثال /sik >> بن از گروه] [ /dsik لغو بن از گروه].
"""

# فحش‌ها برای دشمن
enemy_msgs = [
    "خفه شو دیگه🤣", "سیکتر کن😅", "نبینمت اسکول😂", "برو بچه کیونی🤣🤣",
    "سگ پدر😂", "روانی ریقو🤣", "شاشو😂", "از اینجا تا اونجا توی کو‌..نت😂",
    "ریدم دهنت...😂", "گمشو دیگه بهت خندیدم پرو شدی", "سگو کی باشی😂😂😅",
    "اسکول یه وری", "ریدم تو قیافت", "شاشیدم دهنت😂"
]

def is_admin(user_id):
    return user_id in ADMINS

# دستور /help فقط برای مدیران
@bot.message_handler(commands=['help'])
def show_help(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, help_text)

# /d دستور
@bot.message_handler(commands=['d'])
def d_send(message):
    text = message.text[3:].strip()
    if not text: return
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass
    if message.reply_to_message:
        bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id)
    else:
        bot.send_message(message.chat.id, text)

# /spam دستور
@bot.message_handler(commands=['spam'])
def spam_message(message):
    if not is_admin(message.from_user.id): return
    parts = message.text.split(' ', 2)
    if len(parts) < 3: return
    try:
        count = int(parts[1])
        if count > 100: count = 100
    except: return
    text = parts[2]
    for _ in range(count):
        if message.reply_to_message:
            bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id)
        else:
            bot.send_message(message.chat.id, text)
        time.sleep(0.3)

# /doshman → دشمن کردن
@bot.message_handler(commands=['doshman'])
def doshman_add(message):
    if message.reply_to_message:
        ENEMIES.add(message.reply_to_message.from_user.id)
        bot.reply_to(message, "❗ دشمن فعال شد.")

# /ddoshman → حذف دشمن
@bot.message_handler(commands=['ddoshman'])
def doshman_remove(message):
    if message.reply_to_message:
        ENEMIES.discard(message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ دشمن حذف شد.")

# /mutee سکوت
@bot.message_handler(commands=['mutee'])
def mutee_user(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        try:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=False)
            bot.reply_to(message, "🔇 کاربر در سکوت قرار گرفت.")
        except:
            bot.reply_to(message, "❌ خطا در محدودسازی.")

# /dmutee رفع سکوت
@bot.message_handler(commands=['dmutee'])
def unmute_user(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        try:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=True)
            bot.reply_to(message, "🔊 سکوت برداشته شد.")
        except:
            bot.reply_to(message, "❌ خطا در آزادسازی.")

# /sik → اخراج کاربر
@bot.message_handler(commands=['sik'])
def kick_user(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        try:
            bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.reply_to(message, "⛔ کاربر از گروه حذف شد.")
        except:
            bot.reply_to(message, "❌ خطا در اخراج کاربر.")

# /dsik → رفع اخراج
@bot.message_handler(commands=['dsik'])
def unban_user(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        try:
            bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.reply_to(message, "✅ از لیست بن‌شدگان خارج شد.")
        except:
            bot.reply_to(message, "❌ خطا در آزادسازی.")

# /idd → اطلاعات شخص
@bot.message_handler(commands=['idd'])
def idd_user(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "ندارد"
        bot.reply_to(message, f"📌 اطلاعات کاربر:\n👤 نام: {name}\n🆔 آیدی عددی: `{user.id}`\n🏷 نام کاربری: {username}", parse_mode='Markdown')

# /m معرفی محافظ
@bot.message_handler(commands=['m'])
def introduce_myself(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        intro = (
            "**🛡️ من محافظ اختصاصی این فردم!**\n"
            "بهش دست بزنی، نابودت می‌کنم...\n"
            "حواستو جمع کن، چون من همیشه در سایه‌ها هستم و نظارت می‌کنم 👁‍🗨\n"
            "**یک قدم اشتباه، آخرین قدمته...**\n"
            "#دستیار_محافظتی"
        )
        bot.reply_to(message.reply_to_message, intro, parse_mode='Markdown')

# واکنش به پیام دشمنان
@bot.message_handler(func=lambda m: True)
def reply_to_enemy(m):
    if m.from_user.id in ENEMIES:
        try:
            msg = random.choice(enemy_msgs)
            bot.reply_to(m, msg)
        except:
            pass

bot.infinity_polling()
