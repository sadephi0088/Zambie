import telebot
import time
import threading

TOKEN = '8049022187:AAEoR_IorwWZ8KaH_UMvCo2fa1LjTqhnlWY'
OWNER_ID = 7341748124
ADMINS = {OWNER_ID}

bot = telebot.TeleBot(TOKEN)

doshman_users = set()
muted_users = set()
anti_link_enabled = set()
group_lock_enabled = set()
group_members = set()

doshman_msgs = [
    "خفه شو دیگه🤣", "سیکتر کن😅", "نبینمت اسکول😂", "برو بچه کیونی🤣🤣", "سگ پدر😂",
    "روانی ریقو🤣", "شاشو😂", "از اینجا تا اونجا توی کو‌..نت😂", "ریدم دهنت...😂",
    "گمشو دیگه بهت خندیدم پرو شدی", "سگو کی باشی😂😂😅", "اسکول یه وری",
    "ریدم تو قیافت", "شاشیدم دهنت😂"
]

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
1️⃣2️⃣ /del "پاک کردن پیام‌ها"
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
    return user_id in ADMINS

@bot.message_handler(commands=['help'])
def send_help(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, help_text)

@bot.message_handler(commands=['d'])
def d_handler(message):
    if not is_admin(message.from_user.id):
        return
    text = message.text[3:].strip()
    if text:
        try: bot.delete_message(message.chat.id, message.message_id)
        except: pass
        if message.reply_to_message:
            bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id)
        else:
            bot.send_message(message.chat.id, text)
    else:
        bot.reply_to(message, "❌ مثال: `/d سلام`", parse_mode='Markdown')

@bot.message_handler(commands=['spam'])
def spam_handler(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, count, text = message.text.split(" ", 2)
        count = int(count)
        if count > 100:
            return bot.reply_to(message, "❌ حداکثر 100 بار.")
        for _ in range(count):
            if message.reply_to_message:
                bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id)
            else:
                bot.send_message(message.chat.id, text)
            time.sleep(0.3)
    except:
        bot.reply_to(message, "❌ مثال: `/spam 3 سلام`", parse_mode='Markdown')

@bot.message_handler(commands=['doshman'])
def doshman_on(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        doshman_users.add(message.reply_to_message.from_user.id)
        bot.reply_to(message, "☠️ دشمن فعال شد.")
@bot.message_handler(commands=['ddoshman'])
def doshman_off(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        doshman_users.discard(message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ دشمن غیرفعال شد.")
@bot.message_handler(func=lambda m: m.from_user.id in doshman_users)
def reply_doshman(message):
    text = doshman_msgs[int(time.time()*1000) % len(doshman_msgs)]
    bot.reply_to(message, text)

@bot.message_handler(commands=['mutee'])
def mutee(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        try:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=False)
            bot.reply_to(message, "🔇 کاربر سکوت شد.")
        except:
            bot.reply_to(message, "❌ خطا.")
@bot.message_handler(commands=['dmutee'])
def unmutee(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        try:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=True)
            bot.reply_to(message, "🔊 سکوت برداشته شد.")
        except:
            bot.reply_to(message, "❌ خطا.")

@bot.message_handler(commands=['sik'])
def ban_user(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        try:
            bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.reply_to(message, "🚫 کاربر حذف شد.")
        except:
            bot.reply_to(message, "❌ نشد بندازمش بیرون.")
@bot.message_handler(commands=['dsik'])
def unban_user(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        try:
            bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.reply_to(message, "✅ از لیست بن‌شدگان حذف شد.")
        except:
            bot.reply_to(message, "❌ نشد آزادش کنم.")

@bot.message_handler(commands=['idd'])
def id_info(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        u = message.reply_to_message.from_user
        text = f"👤 نام: {u.first_name}\n🆔 آیدی عددی: `{u.id}`\n📎 یوزرنیم: @{u.username if u.username else 'ندارد'}"
        bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['m'])
def introduce_me(message):
    if is_admin(message.from_user.id):
        txt = "🛡️ من دستیار محافظتی اختصاصی هستم...\nهر حرکتی علیه ارباب من، یعنی اعلام جنگ با من!\n\nبا هر تهدیدی، تو رو از صحنه حذف می‌کنم...\nپس بهتره محتاط باشی و قانون احترام رو رعایت کنی!\n\n#محافظ_شخصی"
        if message.reply_to_message:
            bot.send_message(message.chat.id, txt, reply_to_message_id=message.reply_to_message.message_id)

@bot.message_handler(commands=['zedlink'])
def zedlink_on(message):
    if is_admin(message.from_user.id):
        anti_link_enabled.add(message.chat.id)
        bot.reply_to(message, "🔗 ضد لینک فعال شد.")
@bot.message_handler(commands=['dzedlink'])
def zedlink_off(message):
    if is_admin(message.from_user.id):
        anti_link_enabled.discard(message.chat.id)
        bot.reply_to(message, "🔓 ضد لینک غیرفعال شد.")

@bot.message_handler(commands=['pinn'])
def pin_msg(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        bot.reply_to(message, "📌 پین شد.")
@bot.message_handler(commands=['dpinn'])
def unpin_msg(message):
    if is_admin(message.from_user.id):
        if message.reply_to_message:
            bot.unpin_chat_message(message.chat.id, message.reply_to_message.message_id)
        else:
            bot.unpin_chat_message(message.chat.id)
        bot.reply_to(message, "📍 از پین خارج شد.")

@bot.message_handler(commands=['ghofle'])
def lock_chat(message):
    if is_admin(message.from_user.id):
        group_lock_enabled.add(message.chat.id)
        bot.reply_to(message, "🔒 گروه قفل شد.")
@bot.message_handler(commands=['dghofle'])
def unlock_chat(message):
    if is_admin(message.from_user.id):
        group_lock_enabled.discard(message.chat.id)
        bot.reply_to(message, "🔓 قفل باز شد.")

@bot.message_handler(commands=['del'])
def delete_messages(message):
    if not is_admin(message.from_user.id):
        return
    try:
        count = int(message.text.split()[1])
        for i in range(count):
            bot.delete_message(message.chat.id, message.message_id - i)
        bot.reply_to(message, f"✅ {count} پیام پاک شد.")
    except:
        bot.reply_to(message, "❌ مثال: /del 10")

@bot.message_handler(commands=['adminn'])
def add_admin(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        ADMINS.add(message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ به مدیران ربات افزوده شد.")
@bot.message_handler(commands=['dadminn'])
def remove_admin(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        uid = message.reply_to_message.from_user.id
        if uid != OWNER_ID:
            ADMINS.discard(uid)
            bot.reply_to(message, "⛔ از مدیران حذف شد.")
    else:
        ADMINS.difference_update({uid for uid in ADMINS if uid != OWNER_ID})
        bot.reply_to(message, "⛔ همه مدیران حذف شدند.")

@bot.message_handler(commands=['bgo'])
def bgo(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, "🤖 من آماده‌ام برای محافظت از اربابم!")

# ----------- بخش تگ کردن اعضا ---------------
tagging = False
tag_chat_id = 0
tag_text = ""
tag_thread = None

def tag_members(chat_id, text):
    global tagging
    tagging = True
    try:
        members = bot.get_chat_members_count(chat_id)
        # برای گرفتن اعضا در تلگرام API مستقیم برای گرفتن همه اعضا نداره، فقط میشه مدیرها رو گرفت.
        # اینجا می‌تونیم فقط مدیرها رو تگ کنیم یا اگر تو دیتابیسی اعضا رو ذخیره کردید از اون استفاده کنید.
        admins = bot.get_chat_administrators(chat_id)
        user_ids = [admin.user.id for admin in admins]
        for user_id in user_ids:
            if not tagging:
                break
            try:
                member = bot.get_chat_member(chat_id, user_id).user
                if member.username:
                    mention = f"@{member.username}"
                else:
                    mention = f"[{member.first_name}](tg://user?id={user_id})"
                bot.send_message(chat_id, f"{mention} {text}", parse_mode='Markdown')
                time.sleep(0.3)
            except Exception:
                continue
    finally:
        tagging = False

@bot.message_handler(commands=['tagg'])
def start_tag(message):
    global tag_thread, tag_chat_id, tag_text, tagging
    if not is_admin(message.from_user.id):
        return
    if tagging:
        bot.reply_to(message, "⚠️ عملیات تگ کردن در حال اجراست، ابتدا /stopp را بزنید.")
        return
    tag_chat_id = message.chat.id
    tag_text = message.text[6:].strip() if len(message.text) > 6 else ""
    if message.reply_to_message and tag_text == "":
        tag_text = message.reply_to_message.text or ""
        bot.send_message(tag_chat_id, tag_text, reply_to_message_id=message.reply_to_message.message_id)
    elif tag_text:
        bot.send_message(tag_chat_id, tag_text)
    else:
        bot.send_message(tag_chat_id, "🛡️ توجه: همه اعضا تگ می‌شوند!")
    tag_thread = threading.Thread(target=tag_members, args=(tag_chat_id, tag_text))
    tag_thread.start()

@bot.message_handler(commands=['stopp'])
def stop_tag(message):
    global tagging
    if not is_admin(message.from_user.id):
        return
    if tagging:
        tagging = False
        bot.reply_to(message, "🛑 عملیات تگ کردن متوقف شد.")
    else:
        bot.reply_to(message, "⚠️ عملیات تگ کردن فعال نیست.")

@bot.message_handler(func=lambda message: True)
def auto_check(message):
    if message.chat.id in anti_link_enabled:
        if message.text and any(x in message.text.lower() for x in ['http', 't.me', 'telegram.me', 'www.']):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except: pass
    if message.chat.id in group_lock_enabled:
        if not is_admin(message.from_user.id):
            try: bot.delete_message(message.chat.id, message.message_id)
            except: pass

bot.infinity_polling()
