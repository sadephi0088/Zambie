import telebot
import time
import threading
import sqlite3
import json
import os
from flask import Flask
from telebot import types

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

دیتابیس ذخیره اعضای گروه

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

blacklist_words = [
"بکیرم","کیر","کیرم","کونت","کونی","مادرتو","کص مادرت","کصکش","کسکش","حرومی",
"حرومزاده","کیری","کص ننت","کص پدرت","کونده","خفه شو","جنده","لاشی","سگ",
"گمشو","انتر","ریدم دهنت","ریدم تو قیافت","خارکصه","خوارکصه","خاهرتو","خواهرتو",
"خواهرجنده","خواهر","پدر","مادر","ریدی","گوزو","میگامت","میگام","ننتو","هوی",
"سیکتیر","صیکتیر","پلشت","کونت","عن","مادرجنده"
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

---------- دستورات معمولی -----------

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
bot.reply_to(message, "❌ مثال: /d سلام", parse_mode='Markdown')

---------- بخش یادگیری پاسخ‌ها ----------

learned_replies = {}  # {chat_id: {keyword: reply}}
pending_set = {}      # {user_id: (chat_id, keyword)}

بارگذاری پاسخ‌های ذخیره شده (اگر وجود داشته باشد)

if os.path.exists("replies.json"):
with open("replies.json", "r", encoding="utf-8") as f:
learned_replies = json.load(f)

def save_replies():
with open("replies.json", "w", encoding="utf-8") as f:
json.dump(learned_replies, f, ensure_ascii=False)

---------- بخش دستورات محافظتی و دشمن شناسی ----------

@bot.message_handler(commands=['doshman'])
def doshman_on(message):
global doshman_mode_enabled
if is_admin(message.from_user.id) and message.reply_to_message:
doshman_users.add(message.reply_to_message.from_user.id)
bot.reply_to(message, "☠️ دشمن فعال شد.")

@bot.message_handler(commands=['ddoshman'])
def doshman_off(message):
global doshman_mode_enabled
if is_admin(message.from_user.id) and message.reply_to_message:
doshman_users.discard(message.reply_to_message.from_user.id)
bot.reply_to(message, "✅ دشمن غیرفعال شد.")

@bot.message_handler(commands=['onn'])
def enable_doshman_mode(message):
global doshman_mode_enabled
if is_admin(message.from_user.id):
doshman_mode_enabled = True
bot.reply_to(message, "🟢 دشمن شناسی هوشمند روشن شد.")

@bot.message_handler(commands=['donn'])
def disable_doshman_mode(message):
global doshman_mode_enabled
if is_admin(message.from_user.id):
doshman_mode_enabled = False
bot.reply_to(message, "🔴 دشمن شناسی هوشمند خاموش شد.")

---------- بررسی پیام‌ها برای کلمات بلک لیست ----------

@bot.message_handler(func=lambda m: True)
def check_blacklist(message):
if not doshman_mode_enabled:
return
if not message.reply_to_message:
return  # فقط وقتی ریپلای شده بررسی می‌کنیم
vip_user_id = message.reply_to_message.from_user.id
attacker = message.from_user
text = message.text.lower()
for word in blacklist_words:
if word in text:
# آماده سازی نام یا یوزرنیم برای تگ
if attacker.username:
mention = f"@{attacker.username}"
else:
mention = attacker.first_name
alert_text = f"💀 احساس می‌کنم کاربر {mention} به شما پیغام توهین‌آمیز یا کلماتی زشت فرستاده!\n❗️اگر درست است کافیست با ارسال دستور /doshman + ریپلای روی آن شخص، می‌توانم با فرمان شما نابودش کنم!⚠️"
bot.send_message(vip_user_id, alert_text)
break

---------- ادامه دستورات محافظتی ----------

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
text = f"👤 نام: {u.first_name}\n🆔 آیدی عددی: {u.id}\n📎 یوزرنیم: @{u.username if u.username else 'ندارد'}"
bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['m'])
def introduce_me(message):
if is_admin(message.from_user.id) and message.reply_to_message:
txt = "🛡️ من دستیار محافظتی اختصاصی هستم...\nهر تهدیدی، یعنی اعلام جنگ با من!\n#محافظ_شخصی"
bot.send_message(message.chat.id, txt, reply_to_message_id=message.reply_to_message.message_id)

---------- تگ کردن اعضا ----------

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

---------- وب‌سرور Flask برای keep-alive ----------

app = Flask(name)
@app.route("/")
def home():
return "ربات محافظتی فعال است ❤"

def run_flask():
app.run(host="0.0.0.0", port=8080)

---------- اجرای همزمان Flask و ربات ----------

if name == "main":
threading.Thread(target=run_flask).start()
bot.infinity_polling()

