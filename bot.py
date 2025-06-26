import telebot
import time

TOKEN = '8049022187:AAEoR_IorwWZ8KaH_UMvCo2fa1LjTqhnlWY'
OWNER_ID = 7341748124
ADMINS = {OWNER_ID}

bot = telebot.TeleBot(TOKEN)

def is_admin(user_id):
    return user_id in ADMINS

# 💬 پنل راهنما
help_text = """⚔️ 《 راهنمای ربات محافظتی - نسخه 1.0 》 ⚔️
——————————————————————
🛡️ دستورات اصلی: [محافظت از شما]🩸
1️⃣ /d  ارسال به گروه "جمله شما"
2️⃣ /spam "متن شما" "عدد"
3️⃣ دستور شماره 3
4️⃣ دستور شماره 4
5️⃣ دستور شماره 5
——————————————————————
⚔️ دستورات واکنش به کاربران:👤
6️⃣ دستور شماره 6
7️⃣ دستور شماره 7  
8️⃣ دستور شماره 8
——————————————————————
🔒 دستورات مدیریت گروه:👨‍💻
9️⃣ دستور شماره 9  
🔟 دستور شماره 10
1️⃣1️⃣ دستور شماره 11
——————————————————————
🏷️ سایر دستورات:👾
1️⃣2️⃣ دستور شماره 12
1️⃣3️⃣ دستور شماره 13
——————————————————————
⚠️ توجه:  
تمام دستورات فقط توسط مالک و مدیران ربات قابل اجراست.  
برای لغو دستورات، ابتدای همان دستور بنویسید "d" [مثال /sik >> بن از گروه] [ /dsik لغو بن از گروه].
"""

@bot.message_handler(commands=['help'])
def send_help(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, help_text)

# ✅ دستور اول: /d
@bot.message_handler(commands=['d'])
def d_handler(message):
    if not is_admin(message.from_user.id):
        return

    msg_text = message.text[3:].strip()
    if not msg_text:
        bot.reply_to(message, "❌ لطفاً یک متن بنویس. مثال: `/d سلام خوبی؟`", parse_mode='Markdown')
        return

    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass

    if message.reply_to_message:
        bot.send_message(message.chat.id, msg_text, reply_to_message_id=message.reply_to_message.message_id)
    else:
        bot.send_message(message.chat.id, msg_text)

# ✅ دستور دوم: /spam
@bot.message_handler(commands=['spam'])
def spam_handler(message):
    if not is_admin(message.from_user.id):
        return

    try:
        args = message.text.split(" ", 2)
        count = int(args[1])
        text = args[2]
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ فرمت درست نیست. مثال: `/spam 3 سلام`", parse_mode='Markdown')
        return

    if count > 100:
        bot.reply_to(message, "❌ حداکثر 100 پیام مجاز است.")
        return

    if message.reply_to_message:
        for _ in range(count):
            try:
                bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id)
                time.sleep(0.3)
            except Exception:
                continue
    else:
        for _ in range(count):
            try:
                bot.send_message(message.chat.id, text)
                time.sleep(0.3)
            except Exception:
                continue

bot.infinity_polling()
