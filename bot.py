import telebot

TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
bot = telebot.TeleBot(TOKEN)

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

    proposer_name = f"@{proposer.username}" if proposer.username else proposer.first_name
    target_name = f"@{target.username}" if target.username else target.first_name

    bot.send_message(
        message.chat.id,
        f"💘 تست موفق!\n{proposer_name} دلش پیش {target_name} گیر کرده! 😍\nاگر تو هم حسش رو داری، بگو /accept 💖"
    )

@bot.message_handler(commands=['accept'])
def accept_love(message):
    bot.reply_to(message, "💞 درخواست عشق تستی با موفقیت تایید شد! 🥰")

bot.infinity_polling()
