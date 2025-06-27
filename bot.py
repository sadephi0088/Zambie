import telebot
import time
import threading

TOKEN = '8049022187:AAEoR_IorwWZ8KaH_UMvCo2fa1LjTqhnlWY'
OWNER_ID = 7341748124
ADMINS = {OWNER_ID}
anti_link_chats = set()
admin_user_ids = set()
tagging = False

bot = telebot.TeleBot(TOKEN)

# 💬 پنل راهنما
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
1️⃣2️⃣ /del 5 "پاک‌کردن ۵ پیام اخیر"
——————————————————————
🏷️ سایر دستورات:👾
1️⃣3️⃣ /adminn "افزودن مدیر ربات"
1️⃣4️⃣ /bgo "حرف‌زدن با من"
——————————————————————
⚠️ توجه:  
تمام دستورات فقط توسط مالک و مدیران ربات قابل اجراست.  
برای لغو دستورات، ابتدای همان دستور بنویسید "d" [مثال /sik >> بن از گروه] [ /dsik لغو بن از گروه].
"""

def is_admin(user_id):
    return user_id in ADMINS or user_id in admin_user_ids

# دستور /help
@bot.message_handler(commands=['help'])
def send_help(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, help_text)

# دستور /d
@bot.message_handler(commands=['d'])
def d_handler(message):
    if not is_admin(message.from_user.id): return
    text = message.text[3:].strip()
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass
    if message.reply_to_message:
        bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id)
    else:
        bot.send_message(message.chat.id, text)

# دستور /spam
@bot.message_handler(commands=['spam'])
def spam_handler(message):
    if not is_admin(message.from_user.id): return
    try:
        args = message.text.split(" ", 2)
        count = int(args[1])
        text = args[2]
    except: return
    if count > 100: return
    for _ in range(count):
        try:
            if message.reply_to_message:
                bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id)
            else:
                bot.send_message(message.chat.id, text)
            time.sleep(0.2)
        except: continue

# دستور /doshman و /ddoshman
doshmans = set()
bad_msgs = [
    "خفه شو دیگه🤣", "سیکتر کن😅", "نبینمت اسکول😂", "برو بچه کیونی🤣🤣", "سگ پدر😂", "روانی ریقو🤣",
    "شاشو😂", "از اینجا تا اونجا توی کو‌..نت😂", "ریدم دهنت...😂", "گمشو دیگه بهت خندیدم پرو شدی",
    "سگو کی باشی😂😂😅", "اسکول یه وری", "ریدم تو قیافت", "شاشیدم دهنت😂"
]

@bot.message_handler(commands=['doshman'])
def add_doshman(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        doshmans.add(message.reply_to_message.from_user.id)
        bot.reply_to(message, "☠️ دشمن شناسایی شد.")

@bot.message_handler(commands=['ddoshman'])
def rem_doshman(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        doshmans.discard(message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ دشمن حذف شد.")

# واکنش به دشمن
@bot.message_handler(func=lambda m: True)
def handle_doshman_and_links(m):
    if m.chat.id in anti_link_chats and 'http' in m.text.lower():
        try: bot.delete_message(m.chat.id, m.message_id)
        except: pass
    if m.from_user.id in doshmans:
        try:
            bot.reply_to(m, random.choice(bad_msgs))
        except: pass

# /mutee و /dmutee
@bot.message_handler(commands=['mutee'])
def mutee(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        try:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=False)
            bot.reply_to(message, "🔇 سکوت فعال شد.")
        except: pass

@bot.message_handler(commands=['dmutee'])
def unmutee(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        try:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=True)
            bot.reply_to(message, "🔊 سکوت لغو شد.")
        except: pass

# /sik و /dsik
@bot.message_handler(commands=['sik'])
def ban(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        try:
            bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.reply_to(message, "⛔ کاربر حذف شد.")
        except: pass

@bot.message_handler(commands=['dsik'])
def unban(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        try:
            bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.reply_to(message, "✅ کاربر آزاد شد.")
        except: pass

# /idd
@bot.message_handler(commands=['idd'])
def idd(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        uname = f"@{user.username}" if user.username else "ندارد"
        info = f"👤 نام: {user.first_name}\n🆔 آیدی عددی: `{user.id}`\n🏷 نام کاربری: {uname}"
        bot.reply_to(message, info, parse_mode="Markdown")

# /m
@bot.message_handler(commands=['m'])
def m_handler(message):
    if not is_admin(message.from_user.id): return
    text = "🛡️ من دستیار محافظتی اختصاصی هستم...\nهر حرکتی علیه ارباب من، یعنی اعلام جنگ با من!\n\nبا هر تهدیدی، تو رو از صحنه حذف می‌کنم...\nپس بهتره محتاط باشی و قانون احترام رو رعایت کنی!\n\n#محافظ_شخصی"
    if message.reply_to_message:
        bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id)

# /tagg و /stopp
@bot.message_handler(commands=['tagg'])
def tagg(message):
    global tagging
    if not is_admin(message.from_user.id): return
    text = message.text[6:]
    tagging = True

    def run():
        members = list(ADMINS | admin_user_ids)
        for uid in members:
            if not tagging: break
            try:
                mention = f"@{uid}"
                bot.send_message(message.chat.id, f"{mention} {text}")
                time.sleep(0.5)
            except: continue
    threading.Thread(target=run).start()

@bot.message_handler(commands=['stopp'])
def stopp(message):
    global tagging
    if not is_admin(message.from_user.id): return
    tagging = False
    bot.reply_to(message, "⛔ تگ‌کردن متوقف شد.")

# /zedlink و /dzedlink
@bot.message_handler(commands=['zedlink'])
def zedlink(message):
    if is_admin(message.from_user.id):
        anti_link_chats.add(message.chat.id)
        bot.reply_to(message, "🔒 ضد لینک فعال شد.")

@bot.message_handler(commands=['dzedlink'])
def dzedlink(message):
    if is_admin(message.from_user.id):
        anti_link_chats.discard(message.chat.id)
        bot.reply_to(message, "🔓 ضد لینک غیرفعال شد.")

# /pinn و /dpinn
@bot.message_handler(commands=['pinn'])
def pinn(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)

@bot.message_handler(commands=['dpinn'])
def dpinn(message):
    if is_admin(message.from_user.id):
        if message.reply_to_message:
            bot.unpin_chat_message(message.chat.id, message.reply_to_message.message_id)
        else:
            bot.unpin_all_chat_messages(message.chat.id)

# /ghofle و /dghofle
@bot.message_handler(commands=['ghofle'])
def lock(message):
    if is_admin(message.from_user.id):
        bot.set_chat_permissions(message.chat.id, telebot.types.ChatPermissions(can_send_messages=False))
        bot.reply_to(message, "🔒 گروه قفل شد.")

@bot.message_handler(commands=['dghofle'])
def unlock(message):
    if is_admin(message.from_user.id):
        bot.set_chat_permissions(message.chat.id, telebot.types.ChatPermissions(can_send_messages=True))
        bot.reply_to(message, "🔓 گروه باز شد.")

# /del 10
@bot.message_handler(commands=['del'])
def delete_messages(message):
    if not is_admin(message.from_user.id): return
    try:
        count = int(message.text.split()[1])
        for i in range(count):
            bot.delete_message(message.chat.id, message.message_id - i)
    except: pass

# /adminn و /dadminn
@bot.message_handler(commands=['adminn'])
def admin_add(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        admin_user_ids.add(message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ به لیست مدیران ربات افزوده شد.")

@bot.message_handler(commands=['dadminn'])
def admin_remove(message):
    if message.from_user.id == OWNER_ID:
        if message.reply_to_message:
            admin_user_ids.discard(message.reply_to_message.from_user.id)
            bot.reply_to(message, "⛔ از لیست مدیران حذف شد.")
        else:
            admin_user_ids.clear()
            bot.reply_to(message, "✅ تمام مدیران پاک شدند.")

# /bgo
@bot.message_handler(commands=['bgo'])
def bgo(message):
    bot.reply_to(message, "❤️ بله عشقم، در خدمتتم.")

# شروع
bot.infinity_polling()
