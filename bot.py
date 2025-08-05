import telebot
import time
import threading
import sqlite3
import json
import os
from flask import Flask

TOKEN = '8049022187:AAEoR_IorwWZ8KaH_UMvCo2fa1LjTqhnlWY'
OWNER_ID = 7341748124
ADMINS = {OWNER_ID}
bot = telebot.TeleBot(TOKEN)

doshman_users = set()
muted_users = set()
anti_link_enabled = set()
group_lock_enabled = set()
tagging = False  # کنترل تگ کردن

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
2️⃣ /spam "عدد" "متن"
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
🧠 دستورات یادگیری واکنش‌ها:
1️⃣5️⃣ /set "کلمه"  - تعریف پاسخ برای کلمه (بدون # فقط مدیر)
1️⃣6️⃣ /dset "کلمه" - حذف پاسخ تعریف شده
(کلمات با # برای همه کاربرها قابل استفاده است)
——————————————————————
⚠️ توجه:  
تمام دستورات فقط توسط مالک و مدیران ربات قابل اجراست.
برای لغو دستورات، ابتدای همان دستور بنویسید "d"
"""

def is_admin(user_id):
    return user_id in ADMINS

# ---------- دستورات معمولی -----------
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

# --------------- بخش تگ کردن اعضا ---------------
@bot.message_handler(commands=['tagg'])
def tag_all(message):
    global tagging
    if not is_admin(message.from_user.id):
        return
    if tagging:
        bot.reply_to(message, "⚠️ عملیات تگ کردن در حال اجراست، ابتدا با /stopp متوقفش کن.")
        return

    tagging = True
    tag_text = message.text[6:].strip()
    if message.reply_to_message and tag_text == "":
        tag_text = message.reply_to_message.text or ""

    bot.send_message(message.chat.id, "🛡️ عملیات تگ کردن آغاز شد...")

    cur.execute("SELECT DISTINCT user_id, name FROM members WHERE chat_id = ?", (message.chat.id,))
    members = cur.fetchall()

    for user_id, name in members:
        if not tagging:
            bot.send_message(message.chat.id, "🛑 عملیات تگ کردن متوقف شد.")
            break
        mention = f"[{name}](tg://user?id={user_id})"
        text = f"{mention} {tag_text}"
        if message.reply_to_message:
            bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
        time.sleep(0.4)

    tagging = False
    if tagging == False:
        bot.send_message(message.chat.id, "✅ عملیات تگ کردن به پایان رسید.")

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

# ------------- بخش یادگیری پاسخ‌ها ----------------
learned_replies = {}  # {chat_id: {keyword: reply}}
pending_set = {}      # {user_id: (chat_id, keyword)}

# بارگذاری پاسخ‌های ذخیره شده (اگر وجود داشته باشد)
if os.path.exists("replies.json"):
    with open("replies.json", "r", encoding="utf-8") as f:
        learned_replies = json.load(f)

def save_replies():
    with open("replies.json", "w", encoding="utf-8") as f:
        json.dump(learned_replies, f, ensure_ascii=False)

@bot.message_handler(commands=['set'])
def handle_set_command(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "⛔ فقط مدیران می‌تونن کلمات بدون # رو تعریف کنند.")
    parts = message.text.split(" ", 1)
    if len(parts) < 2 or parts[1].strip() == "":
        return bot.reply_to(message, "❌ مثال: `/set سلام`", parse_mode="Markdown")
    keyword = parts[1].strip()
    pending_set[message.from_user.id] = (message.chat.id, keyword)
    bot.reply_to(message, f"🔁 لطفاً پاسخ برای کلمه «{keyword}» را در پیام بعدی ارسال کن.")

@bot.message_handler(commands=['dset'])
def handle_dset_command(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(" ", 1)
    if len(parts) < 2 or parts[1].strip() == "":
        return bot.reply_to(message, "❌ مثال: `/dset سلام`", parse_mode="Markdown")
    keyword = parts[1].strip()
    chat_id = str(message.chat.id)
    if chat_id in learned_replies and keyword in learned_replies[chat_id]:
        del learned_replies[chat_id][keyword]
        save_replies()
        bot.reply_to(message, f"✅ پاسخ برای کلمه «{keyword}» حذف شد.")
    else:
        bot.reply_to(message, "❌ چنین کلمه‌ای تعریف نشده است.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # ذخیره عضو در دیتابیس
    save_member(message.chat.id, message.from_user)

    # اگر منتظر پاسخ هستیم (مرحله set)
    if message.from_user.id in pending_set:
        chat_id, keyword = pending_set.pop(message.from_user.id)
        chat_id = str(chat_id)
        if chat_id not in learned_replies:
            learned_replies[chat_id] = {}
        learned_replies[chat_id][keyword] = message.text
        save_replies()
        bot.reply_to(message, f"✅ پاسخ برای «{keyword}» ذخیره شد.")
        return

    # بررسی و پاسخ خودکار به کلمات تعریف شده
    chat_id = str(message.chat.id)
    if chat_id in learned_replies:
        for keyword, reply in learned_replies[chat_id].items():
            if keyword.startswith("#"):  # اگر هشتگ داشت همه می‌تونن جواب بگیرن
                if keyword in message.text:
                    bot.reply_to(message, reply)
                    return
            else:  # اگر بدون هشتگ بود فقط مدیران می‌تونن جواب بگیرن
                if keyword in message.text and message.from_user.id in ADMINS:
                    bot.reply_to(message, reply)
                    return

# حذف عضو از دیتابیس وقتی ترک میده گروه
@bot.my_chat_member_handler()
def handle_member_update(message):
    if message.old_chat_member.status in ['member', 'administrator', 'creator'] and message.new_chat_member.status == 'left':
        user_id = message.new_chat_member.user.id
        remove_member(message.chat.id, user_id)

# چک کردن ضد لینک
@bot.message_handler(func=lambda m: True)
def check_links_and_lock(message):
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

# ----------- اضافه کردن وب‌سرور Flask برای keep-alive ------------
app = Flask(__name__)

@app.route("/")
def home():
    return "ربات محافظتی فعال است ❤"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# اجرای همزمان فلاسک و ربات
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
