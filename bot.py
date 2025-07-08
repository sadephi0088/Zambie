import telebot
from telebot.types import Message

bot = telebot.TeleBot("7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs")

# حالت خوش‌آمدگویی (روشن/خاموش)
welcome_enabled = True

# روشن کردن خوش‌آمدگویی با /wlc
@bot.message_handler(commands=['wlc'])
def enable_welcome(message: Message):
    global welcome_enabled
    welcome_enabled = True
    bot.reply_to(message, "✅ خوش‌آمدگویی روشن شد.")

# خاموش کردن خوش‌آمدگویی با /dwlc
@bot.message_handler(commands=['dwlc'])
def disable_welcome(message: Message):
    global welcome_enabled
    welcome_enabled = False
    bot.reply_to(message, "❌ خوش‌آمدگویی خاموش شد.")

# اجرای خوش‌آمدگویی هنگام ورود
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message: Message):
    global welcome_enabled
    if not welcome_enabled:
        return

    for user in message.new_chat_members:
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        user_id = user.id
        username = f"@{user.username}" if user.username else "ندارد ❌"

        welcome_text = f"""╔═━⊱🌟 TikTak • پیام ورود 🌟⊰━═╗  
🎉 خوش‌آمدی {full_name} عزیز! 🎉  

🆔 آیدی: {user_id}  
🔗 یوزرنیم: {username}

━━━━━━━━━━━━━━━━━━  

📄 پروفایل اختصاصی‌ت ساخته شد!  
🎭 قدرت‌هات، افتخاراتت، امتیازاتت... همه اینجانست!
👁‍🗨 برای دیدنش، فقط توی گروه بنویس:  
/mee   👈
━━━━━━━━━━━━━━━━━━  
🌟 با عشق، تیم مدیریت TikTak Master"""

        # ریپلای روی پیام ورود خود تلگرام
        bot.send_message(message.chat.id, welcome_text, reply_to_message_id=message.message_id)

bot.infinity_polling()
