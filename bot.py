import telebot
import random
import threading
import time

TOKEN = '8049022187:AAEoR_IorwWZ8KaH_UMvCo2fa1LjTqhnlWY'
OWNER_ID = 7341748124
ADMINS = {OWNER_ID}

bot = telebot.TeleBot(TOKEN)

mozahem_users = set()
doshaman_users = set()
group_members = set()
anti_link_enabled = set()
group_lock_enabled = set()

tagging = False
tagged_message_ids = []
tag_text = ""
tag_chat_id = 0
tag_thread = None

hoi_reply = "**👁‍🗨 نگاهت، رفتارت، حضورت... تحت نظرمه! مراقب باش.**"
hosh_reply = "**⚠️ آخرین اخطار! ادامه بدی... حمله می‌کنم!**"
ghanon_text = "**📜 قانون خون و سایه‌ها رو رعایت کن یا از بین می‌ری!**"

mozahem_msgs = ["باز مزاحم شدی؟ 😒", "داری اعصاب منو بهم می‌ریزی! ⚠️", "ول کن دیگه! 🤬"]
doshaman_msgs = ["لعنتی، وقت نابودیه! 💣", "تو دشمنی! نابودت می‌کنم! 🔥", "گمشو از جلوی چشمم! 👿"]

help_text = """⚔ **《 راهنما زامبی-محافظت از شما 》** ⚔
——————————————————————
🔰 **هشدارها:**
  /hoi     ▶ هشدار اولیه (ریپلای کن)
  /hosh    ▶ اخطار نهایی (ریپلای کن)
  /ghanon  ▶ لزوم رعایت قانون
——————————————————————
😈 **واکنش به مزاحمین:**
  /mozahem   ▶ مزاحم شد (ریپلای کن)
  /dmozahem  ▶ حذف مزاحم (ریپلای کن)
——————————————————————
💀 **نابود کردن دشمنان:**
  /doshaman  ▶ حمله به دشمن (ریپلای کن)
  /ddoshman  ▶ لغو حمله (ریپلای کن)
  /bann      ▶ بن از گروه (ریپلای کن)
  /mutee     ▶ سکوت دائم (ریپلای کن)
  /unmutt    ▶ لغو سکوت (ریپلای کن)
——————————————————————
📌 **سنجاق پیام‌ها:**
  /pinn      ▶ سنجاق پیام (ریپلای کن)
  /unpin     ▶ حذف سنجاق (ریپلای کن)
——————————————————————
🏷️ **تگ کردن اعضا:**
  /tagg [متن] ▶ تگ همه اعضا با متن دلخواه
  /stopp      ▶ توقف تگ و حذف پیام‌های تگ شده
——————————————————————
🔒 **قفل و ضد لینک:**
  /zedlink   ▶ فعال کردن ضد لینک
  /dzedlink  ▶ غیرفعال کردن ضد لینک
  /ghofle    ▶ قفل گروه
  /dghofle   ▶ بازکردن گروه
——————————————————————
⚙️ **مدیریت:**
  /adminn    ▶ ارتقای فرد به مدیر (ریپلای کن)
  /dadminn   ▶ حذف مدیر (ریپلای کن)
  /idd       ▶ اطلاعات کاربر (ریپلای کن)
——————————————————————
🩸 **#زامبی_نگهبان نسخه 1.1.0**
"""

def is_admin(user_id):
    return user_id in ADMINS

@bot.message_handler(func=lambda m: True)
def catch_users(m):
    if m.chat.type in ['group', 'supergroup']:
        group_members.add(m.from_user.id)

@bot.message_handler(commands=['idd'])
def user_info(message):
    if not is_admin(message.from_user.id): return
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        uid = user.id
        uname = f"@{user.username}" if user.username else "ندارد"
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        text = f"📌 اطلاعات کاربر:\n👤 نام: {name}\n🏷 یوزرنیم: {uname}\n🆔 آیدی عددی: `{uid}`"
        bot.reply_to(message, text, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❗ لطفاً روی پیام کاربر ریپلای کن.")

@bot.message_handler(commands=['help'])
def help_handler(m):
    if is_admin(m.from_user.id): bot.reply_to(m, help_text)

@bot.message_handler(commands=['hoi'])
def hoi(m): 
    if m.reply_to_message: bot.reply_to(m.reply_to_message, hoi_reply)

@bot.message_handler(commands=['hosh'])
def hosh(m): 
    if m.reply_to_message: bot.reply_to(m.reply_to_message, hosh_reply)

@bot.message_handler(commands=['ghanon'])
def ghanon(m): bot.reply_to(m, ghanon_text)

@bot.message_handler(commands=['mozahem'])
def mozahem(m):
    if m.reply_to_message:
        mozahem_users.add(m.reply_to_message.from_user.id)
        bot.reply_to(m, "✅ مزاحم شناسایی شد.")

@bot.message_handler(commands=['dmozahem'])
def dmozahem(m):
    if m.reply_to_message:
        mozahem_users.discard(m.reply_to_message.from_user.id)
        bot.reply_to(m, "🗑 مزاحم حذف شد.")

@bot.message_handler(commands=['doshaman'])
def doshaman(m):
    if m.reply_to_message:
        doshaman_users.add(m.reply_to_message.from_user.id)
        bot.reply_to(m, "💀 دشمن فعال شد.")

@bot.message_handler(commands=['ddoshman'])
def ddoshman(m):
    if m.reply_to_message:
        doshaman_users.discard(m.reply_to_message.from_user.id)
        bot.reply_to(m, "✅ دشمن حذف شد.")

@bot.message_handler(commands=['bann'])
def bann(m):
    if m.reply_to_message and is_admin(m.from_user.id):
        try:
            bot.ban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
            bot.reply_to(m, "⛔ کاربر بن شد.")
        except: bot.reply_to(m, "❌ خطا در بن.")

@bot.message_handler(commands=['mutee'])
def mutee(m):
    if m.reply_to_message and is_admin(m.from_user.id):
        try:
            bot.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id, can_send_messages=False)
            bot.reply_to(m, "🔇 کاربر ساکت شد.")
        except: bot.reply_to(m, "❌ خطا در سکوت.")

@bot.message_handler(commands=['unmutt'])
def unmutt(m):
    if m.reply_to_message and is_admin(m.from_user.id):
        try:
            bot.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id, can_send_messages=True)
            bot.reply_to(m, "🔊 سکوت برداشته شد.")
        except: bot.reply_to(m, "❌ خطا در آزادسازی.")

@bot.message_handler(commands=['pinn'])
def pinn(m):
    if m.reply_to_message and is_admin(m.from_user.id):
        try:
            bot.pin_chat_message(m.chat.id, m.reply_to_message.message_id)
            bot.reply_to(m, "📌 پیام سنجاق شد.")
        except: bot.reply_to(m, "❌ خطا در سنجاق.")

@bot.message_handler(commands=['unpin'])
def unpin(m):
    if is_admin(m.from_user.id):
        try:
            bot.unpin_chat_message(m.chat.id)
            bot.reply_to(m, "📍 سنجاق حذف شد.")
        except: bot.reply_to(m, "❌ خطا در حذف سنجاق.")

def tagging_thread():
    global tagging
    for uid in list(group_members):
        if not tagging: break
        try:
            msg = bot.send_message(tag_chat_id, f"👤 [کاربر](tg://user?id={uid}) {tag_text}", parse_mode='Markdown')
            tagged_message_ids.append(msg.message_id)
            time.sleep(0.4)
        except: continue
    tagging = False

@bot.message_handler(commands=['tagg'])
def tagg(m):
    global tagging, tag_text, tag_chat_id, tagged_message_ids, tag_thread
    if not is_admin(m.from_user.id): return
    if tagging: return bot.reply_to(m, "⏳ در حال تگ هستم...")
    tag_text = m.text[6:].strip()
    tag_chat_id = m.chat.id
    tagging = True
    tagged_message_ids = []
    tag_thread = threading.Thread(target=tagging_thread)
    tag_thread.start()
    bot.reply_to(m, "🏷 شروع تگ کردن...")

@bot.message_handler(commands=['stopp'])
def stopp(m):
    global tagging
    if not is_admin(m.from_user.id): return
    tagging = False
    for mid in tagged_message_ids:
        try: bot.delete_message(tag_chat_id, mid)
        except: pass
    tagged_message_ids.clear()
    bot.reply_to(m, "🛑 تگ متوقف شد.")

@bot.message_handler(commands=['zedlink'])
def zedlink(m):
    if is_admin(m.from_user.id):
        anti_link_enabled.add(m.chat.id)
        bot.reply_to(m, "🔒 ضد لینک فعال شد.")

@bot.message_handler(commands=['dzedlink'])
def dzedlink(m):
    if is_admin(m.from_user.id):
        anti_link_enabled.discard(m.chat.id)
        bot.reply_to(m, "🔓 ضد لینک غیرفعال شد.")

@bot.message_handler(commands=['ghofle'])
def ghoffle(m):
    if is_admin(m.from_user.id):
        group_lock_enabled.add(m.chat.id)
        bot.reply_to(m, "🔐 گروه قفل شد.")

@bot.message_handler(commands=['dghofle'])
def dghoffle(m):
    if is_admin(m.from_user.id):
        group_lock_enabled.discard(m.chat.id)
        bot.reply_to(m, "🔓 قفل گروه باز شد.")

@bot.message_handler(commands=['adminn'])
def addadmin(m):
    if m.reply_to_message and m.from_user.id == OWNER_ID:
        ADMINS.add(m.reply_to_message.from_user.id)
        bot.reply_to(m, "✅ مدیر شد.")

@bot.message_handler(commands=['dadminn'])
def deladmin(m):
    if m.reply_to_message and m.from_user.id == OWNER_ID:
        ADMINS.discard(m.reply_to_message.from_user.id)
        bot.reply_to(m, "❌ از مدیریت حذف شد.")

@bot.message_handler(func=lambda m: True)
def check_messages(m):
    if m.chat.type in ['group', 'supergroup']:
        if m.chat.id in anti_link_enabled and any(x in m.text.lower() for x in ['http://', 'https://', 't.me', 'telegram.me', 'www.']):
            try:
                bot.delete_message(m.chat.id, m.message_id)
                return
            except: pass
        if m.chat.id in group_lock_enabled and not is_admin(m.from_user.id):
            try:
                bot.delete_message(m.chat.id, m.message_id)
                return
            except: pass
    if m.from_user.id in mozahem_users:
        bot.reply_to(m, random.choice(mozahem_msgs))
    elif m.from_user.id in doshaman_users:
        bot.reply_to(m, random.choice(doshaman_msgs))

bot.infinity_polling()
