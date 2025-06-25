@bot.message_handler(commands=['idd'])
def user_info(message):
    if not is_admin(message.from_user.id):
        return
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        user_id = user.id
        user_name = f"@{user.username}" if user.username else "(ندارد)"
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        full_name = (first_name + " " + last_name).strip()
        text = f"📌 اطلاعات کاربر:\n" \
               f"👤 نام: {full_name}\n" \
               f"🆔 آیدی عددی: `{user_id}`\n" \
               f"🏷 نام کاربری: {user_name}\n"
        try:
            photos = bot.get_user_profile_photos(user_id)
            if photos.total_count > 0:
                photo = photos.photos[0][-1]
                bot.send_photo(message.chat.id, photo.file_id, caption=text, reply_to_message_id=message.message_id)
            else:
                bot.reply_to(message, text)
        except Exception:
            bot.reply_to(message, text)
    else:
        bot.reply_to(message, "❌ لطفا روی پیام فرد مورد نظر ریپلای کن.")
