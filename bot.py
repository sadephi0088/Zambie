import telebot
import time
import threading
import sqlite3

TOKEN = '8049022187:AAEoR_IorwWZ8KaH_UMvCo2fa1LjTqhnlWY'
OWNER_ID = 7341748124
ADMINS = {OWNER_ID}
bot = telebot.TeleBot(TOKEN)

doshman_users = set()
muted_users = set()
anti_link_enabled = set()
group_lock_enabled = set()
tagging = False

# دیتابیس ذخیره اعضای گروه
conn = sqlite3.connect("members.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS members (chat_id INTEGER, user_id INTEGER, name TEXT)")
conn.commit()

def save_member(chat_id, user):
    cur.execute("INSERT OR IGNORE INTO members (chat_id, user_id, name) VALUES (?, ?, ?)",
                (chat_id, user.id, user.first_name))
    conn.commit()

def remove_member(chat_id, user_id):
    cur.execute("DELETE FROM members WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
    conn.commit()

doshman_msgs = [
    "خفه شو دیگه🤣", "سیکتر کن😅", "نبینمت اسکول😂", "برو بچه کیونی🤣🤣", "سگ پدر😂",
    "روانی ریقو🤣", "شاشو😂", "از اینجا تا اونجا توی کو‌..نت😂", "ریدم دهنت...😂",
    "گمشو دیگه بهت خندیدم پرو شدی", "سگو کی باشی😂😂😅", "اسکول یه وری", "ریدم تو قیافت", "شاشیدم دهنت😂"
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
برای لغو دستورات، ابتدای همان دستور بنویسید "d"
"""

def is_admin(user_id):
    return user_id in ADMINS

@bot.message_handler(commands=['help'])
def send_help(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, help_text)

@bot.message_handler(commands=['d'])
def d_handler(message):
    if not is_admin(message.from_user.id): return
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
    if not is_admin(message.from_user.id): return
    try:
        _, count, text = message.text.split(" ", 2)
        count = int(count)
        if count > 100:
            return bot.reply_to(message, "❌ حداکثر 100 بار.")
        for _ in range(count):
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
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=False)
        bot.reply_to(message, "🔇 کاربر سکوت شد.")
@bot.message_handler(commands=['dmutee'])
def unmutee(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=True)
        bot.reply_to(message, "🔊 سکوت برداشته شد.")

@bot.message_handler(commands=['sik'])
def ban_user(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        bot.reply_to(message, "🚫 کاربر حذف شد.")
@bot.message_handler(commands=['dsik'])
def unban_user(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ از لیست بن‌شدگان حذف شد.")

@bot.message_handler(commands=['idd'])
def id_info(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        u = message.reply_to_message.from_user
        text = f"👤 نام: {u.first_name}\n🆔 آیدی عددی: `{u.id}`\n📎 یوزرنیم: @{u.username if u.username else 'ندارد'}"
        bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['m'])
def introduce_me(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        txt = "🛡️ من دستیار محافظتی اختصاصی هستم...\nهر تهدیدی، یعنی اعلام جنگ با من!\n#محافظ_شخصی"
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
    if not is_admin(message.from_user.id): return
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
        bot.reply_to(message, "✅ به مدیران افزوده شد.")
@bot.message_handler(commands=['dadminn'])
def remove_admin(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        ADMINS.discard(message.reply_to_message.from_user.id)
        bot.reply_to(message, "⛔ از مدیران حذف شد.")

@bot.message_handler(commands=['bgo'])
def bgo(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, "🤖 من آماده‌ام برای محافظت از اربابم!")

# ---------------- تگ اعضا ----------------
@bot.message_handler(commands=['tagg'])
def tag_all(message):
    if not is_admin(message.from_user.id): return
    tag_text = message.text[6:].strip()
    bot.send_message(message.chat.id, "🛡️ عملیات تگ کردن اعضا آغاز شد!")
    cur.execute("SELECT DISTINCT user_id, name FROM members WHERE chat_id = ?", (message.chat.id,))
    members = cur.fetchall()
    for user_id, name in members:
        try:
            mention = f"[{name}](tg://user?id={user_id}) {tag_text}"
            if message.reply_to_message:
                bot.send_message(message.chat.id, mention, reply_to_message_id=message.reply_to_message.message_id, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, mention, parse_mode="Markdown")
            time.sleep(0.4)
        except:
            continue

@bot.message_handler(func=lambda message: True)
def all_messages(message):
    save_member(message.chat.id, message.from_user)
    if message.chat.id in anti_link_enabled:
        if message.text and any(x in message.text.lower() for x in ['http', 't.me', 'telegram.me', 'www.']):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
    if message.chat.id in group_lock_enabled:
        if not is_admin(message.from_user.id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass

# حذف عضو هنگام خروج از گروه
@bot.message_handler(content_types=['left_chat_member'])
def on_user_left(message):
    left_user = message.left_chat_member
    remove_member(message.chat.id, left_user.id)

bot.infinity_polling()
