import telebot
import time
import random

TOKEN = '8049022187:AAEoR_IorwWZ8KaH_UMvCo2fa1LjTqhnlWY'
OWNER_ID = 7341748124
ADMINS = {OWNER_ID}
ENEMIES = set()

bot = telebot.TeleBot(TOKEN)

def is_admin(user_id):
    return user_id in ADMINS

# پنل راهنما
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

# فحش‌ها برای دشمنان
insults = [
    "خفه شو دیگه🤣",
    "سیکتر کن😅",
    "نبینمت اسکول😂",
    "برو بچه کیونی🤣🤣",
    "سگ پدر😂",
    "روانی ریقو🤣",
    "شاشو😂",
    "از اینجا تا اونجا توی کو‌..نت😂",
    "ریدم دهنت...😂",
    "گمشو دیگه بهت خندیدم پرو شدی",
    "سگو کی باشی😂😂😅",
    "اسکول یه وری",
    "ریدم تو قیافت",
    "شاشیدم دهنت😂"
]

@bot.message_handler(commands=['help'])
def send_help(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, help_text)

# /d
@bot.message_handler(commands=['d'])
def d_handler(message):
    if not is_admin(message.from_user.id): return
    msg_text = message.text[3:].strip()
    if not msg_text:
        bot.reply_to(message, "❌ لطفاً یک متن بنویس. مثال: `/d سلام خوبی؟`", parse_mode='Markdown')
        return
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass
    if message.reply_to_message:
        bot.send_message(message.chat.id, msg_text, reply_to_message_id=message.reply_to_message.message_id)
    else:
        bot.send_message(message.chat.id, msg_text)

# /spam
@bot.message_handler(commands=['spam'])
def spam_handler(message):
    if not is_admin(message.from_user.id): return
    try:
        args = message.text.split(" ", 2)
        count = int(args[1])
        text = args[2]
    except:
        bot.reply_to(message, "❌ فرمت درست نیست. مثال: `/spam 3 سلام`", parse_mode='Markdown')
        return
    if count > 100:
        bot.reply_to(message, "❌ حداکثر 100 پیام مجاز است.")
        return
    for _ in range(count):
        try:
            if message.reply_to_message:
                bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id)
            else:
                bot.send_message(message.chat.id, text)
            time.sleep(0.3)
        except:
            continue

# /mutee
@bot.message_handler(commands=['mutee'])
def mutee_handler(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        try:
            bot.restrict_chat_member(
                message.chat.id,
                message.reply_to_message.from_user.id,
                can_send_messages=False
            )
            bot.reply_to(message, "🔇 کاربر سکوت دائمی شد.")
        except:
            bot.reply_to(message, "❌ خطا در سکوت کاربر.")

# /dmutee
@bot.message_handler(commands=['dmutee'])
def dmutee_handler(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        try:
            bot.restrict_chat_member(
                message.chat.id,
                message.reply_to_message.from_user.id,
                can_send_messages=True
            )
            bot.reply_to(message, "🔊 سکوت کاربر برداشته شد.")
        except:
            bot.reply_to(message, "❌ خطا در آزادسازی سکوت کاربر.")

# /doshman → اضافه به لیست دشمنان
@bot.message_handler(commands=['doshman'])
def doshman_handler(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        ENEMIES.add(message.reply_to_message.from_user.id)
        bot.reply_to(message, "☠️ کاربر به عنوان دشمن ثبت شد.")

# /ddoshman → حذف از لیست دشمنان
@bot.message_handler(commands=['ddoshman'])
def ddoshman_handler(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        ENEMIES.discard(message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ کاربر از لیست دشمنان حذف شد.")

# /sik → بن کردن کاربر
@bot.message_handler(commands=['sik'])
def sik_handler(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        try:
            bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.reply_to(message, "⛔ کاربر از گروه حذف شد.")
        except:
            bot.reply_to(message, "❌ خطا در حذف کاربر.")

# واکنش به دشمنان با فحش
@bot.message_handler(func=lambda m: True)
def respond_to_enemies(message):
    if message.from_user.id in ENEMIES:
        try:
            bot.send_message(
                message.chat.id,
                random.choice(insults),
                reply_to_message_id=message.message_id
            )
        except:
            pass

bot.infinity_polling()
