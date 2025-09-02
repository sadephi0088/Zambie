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
doshman_mode_enabled = True  # روشن/خاموش دشمن شناسی

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

help_text = """☣✨ 𝑷𝑶𝑾𝑬𝑹 𝑷𝑨𝑵𝑬𝑳 - نسخه 2.0☣  
⛓‍💥"اکنون قدرت مطلق در دستان توست..."🫡⛓‍💥

════════════════════
🧠 ︙یادگیری و واکنش خودکارم:  
➤ /set "کلمه" – تعریف پاسخ برای کلمه (بدون # برای مدیران)  
➤ /dset "کلمه" – حذف پاسخ تعریف‌شده  
💡 کلمات با # برای همه قابل استفاده هستن
════════════════════
🛡️ ︙دستورات محافظت خشن از شما:  
➤ /d 💥 جای تو حرف می‌زنم  
➤ /spam ☢️ رگبار پیام + تعداد  
➤ /doshman 🩸 نابودی دشمنان  
➤ /mutee 🧨 سکوت مطلق هدف  
➤ /sik ☠️ سیکتیر از گروه
════════════════════
🎯 ︙دستورات واکنشی:  
➤ /idd 📯شناسایی و گزارش هدف  
➤ /tagg 🚨 صدا زدن همه‌ی اعضا
════════════════════
👁️‍🗨️︙امنیت و مدیریت گروه:  
➤ /zedlink 🔒 فعال‌سازی ضد لینک  
➤ /pinn 📌 پین کردن پیام  
➤ /del 🧽 حذف پیام + تعداد
════════════════════
🕷️︙فرمان‌های ویژه سازنده:  
➤ /adminn 🧛 افزودن فرد برای محافظت   
➤ /bgo 🕯️ هدف از حضور من چیست؟
════════════════════
🔱 𝑽𝒆𝒓𝒔𝒊𝒐𝒏: 1.0  
⚡ قدرت مطلق = با یک فرمان شما...☣
"""

def is_admin(user_id):
    return user_id in ADMINS

# ----------------- دستورات اصلی -----------------
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

# ----------------- دشمن شناسی -----------------
@bot.message_handler(commands=['doshman'])
def doshman_on_cmd(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        doshman_users.add(message.reply_to_message.from_user.id)
        bot.reply_to(message, "☠️ دشمن فعال شد.")

@bot.message_handler(commands=['ddoshman'])
def doshman_off_cmd(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        doshman_users.discard(message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ دشمن غیرفعال شد.")

@bot.message_handler(commands=['onn'])
def enable_doshman_mode(message):
    global doshman_mode_enabled
    if is_admin(message.from_user.id):
        doshman_mode_enabled = True
        bot.reply_to(message, "🟢 دشمن شناسی روشن شد.")

@bot.message_handler(commands=['donn'])
def disable_doshman_mode(message):
    global doshman_mode_enabled
    if is_admin(message.from_user.id):
        doshman_mode_enabled = False
        bot.reply_to(message, "🔴 دشمن شناسی خاموش شد.")

# ----------------- تگ کردن اعضا -----------------
tagging_pending = False
@bot.message_handler(commands=['tagg'])
def tag_all(message):
    global tagging
    if not is_admin(message.from_user.id): return
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
    bot.send_message(message.chat.id, "✅ عملیات تگ کردن به پایان رسید.")

@bot.message_handler(commands=['stopp'])
def stop_tag(message):
    global tagging
    if not is_admin(message.from_user.id): return
    if tagging:
        tagging = False
        bot.reply_to(message, "🛑 عملیات تگ کردن متوقف شد.")
    else:
        bot.reply_to(message, "⚠️ عملیات تگ کردن فعال نیست.")

# ----------------- یادگیری پاسخ‌ها -----------------
learned_replies = {}
pending_set = {}
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
    if not is_admin(message.from_user.id): return
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
    save_member(message.chat.id, message.from_user)
    # پردازش دشمن‌ها
    if doshman_mode_enabled and message.reply_to_message:
        vip_id = message.reply_to_message.from_user.id
        if message.from_user.id in doshman_users:
            reply_text = doshman_msgs[int(time.time()*1000) % len(doshman_msgs)]
            bot.reply_to(message, reply_text)
        else:
            mention = message.from_user.first_name
            alert_text = f"💀 کاربر {mention} به شما پیام فرستاده!\n❗️اگر می‌خواید نابودش کنید، ریپلای کنید و /doshman بزنید."
            try: bot.send_message(vip_id, alert_text)
            except: pass

    if message.from_user.id in pending_set:
        chat_id, keyword = pending_set.pop(message.from_user.id)
        chat_id = str(chat_id)
        if chat_id not in learned_replies:
            learned_replies[chat_id] = {}
        learned_replies[chat_id][keyword] = message.text
        save_replies()
        bot.reply_to(message, f"✅ پاسخ برای «{keyword}» ذخیره شد.")
        return

    chat_id = str(message.chat.id)
    if chat_id in learned_replies:
        for keyword, reply in learned_replies[chat_id].items():
            if keyword.startswith("#"):
                if keyword in message.text:
                    bot.reply_to(message, reply)
                    return
            else:
                if keyword in message.text and message.from_user.id in ADMINS:
                    bot.reply_to(message, reply)
                    return

# ----------------- حذف عضو -----------------
@bot.my_chat_member_handler()
def handle_member_update(message):
    if message.old_chat_member.status in ['member', 'administrator', 'creator'] and message.new_chat_member.status == 'left':
        user_id = message.new_chat_member.user.id
        remove_member(message.chat.id, user_id)

# ----------------- ضد لینک و قفل گروه -----------------
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

# ----------------- Flask keep-alive -----------------
app = Flask(__name__)
@app.route("/")
def home():
    return "ربات محافظتی فعال است ❤"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
