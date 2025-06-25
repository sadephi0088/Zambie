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

mozahem_msgs = [
    "اوه اوه! باز داره مزاحمت می‌کنه، چرا اینقدر به خودت مطمئنی؟! 😂",
    "چی شد؟ باز حرف‌های تکراری؟ نکنه کم آوردی؟! 🙃",
    "هه! فکر کردی کسی گوش می‌کنه؟ بیشتر تلاش کن، هنوز راه داری! 😏",
    "این همه پیام می‌فرستی، انگار منتظر جایزه‌ای! 🏆",
    "مزاحمت مثل یک ویروس شده، باید واکسینه بشی! 🤒",
    "باز هم مزاحم شدی؟ داری جایزه‌ات رو می‌گیری! 🎉",
    "حرفات مثه صدای وزوز پشه‌ست، مزاحمی بی‌وقفه! 🦟",
    "اگه خسته شدی، به من بگو، من ادامه می‌دم! 😈",
    "آخه این همه پیام برای چی؟ دارم فکر می‌کنم برای کی می‌نویسی! 🤔",
    "زود باش، وقتشه که به اشتباهاتت پی ببری! ⏳",
    "یه چیزی می‌گم، ولی بهتره فراموشش کنی! 😂",
    "تو مزاحم هستی و من تماشاگر، مسابقه‌ی پر سر و صدا! 🎭"
]

doshaman_msgs = [
    "بیشعور کودن وقتشه بسوزونمت!",
    "عوضی اشغال 😂😂 زجه بزن",
    "از اینجا تا داهاتت لاله کاشتم میان لاله‌ها کو*نت گذاشتم 😂",
    "هررری دوهزاری",
    "ریقوو ریدی",
    "احمق رو 😂😂🤣",
    "چقدر کصافتی 🤣",
    "شغال گورتو گم کن نبینمت",
    "پسی خور جمع 🤣🤣",
    "انگشتی جمع 😂😂🤣",
    "لال شو دیگه",
    "از رو نرفتی جدی؟ 🤣🤣",
    "عن تو دهنت 😅",
    "از قیافت بدم اومد 🤣",
    "اعتماد به نفستو.... 🤣",
    "شاشو گورت کجا بود کفنت باشه",
    "پاشو پاشو جمش کن تخم...😅🤣",
    "باید بگی گو خوردم ولت کنم",
    "تا نگی گو خوردم ولت نمیکنم 🤣",
    "اخ دهنتو ساییدم... کاری ازت بر نیومد😅🤣"
]

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
  /mutee     ▶ سکوت دائمی (ریپلای کن)
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
  /zedlink   ▶ فعال کردن ضد لینک (پاک‌سازی لینک‌ها)
  /dzedlink  ▶ غیرفعال کردن ضد لینک
  /ghofle    ▶ قفل گروه (فقط مدیران پیام میدن)
  /dghofle   ▶ بازکردن قفل گروه
——————————————————————
⚙️ **مدیریت:**
  /adminn    ▶ ارتقای فرد به مدیر ربات (ریپلای کن)
  /dadminn   ▶ حذف فرد از مدیریت (ریپلای کن)
  /idd       ▶ نمایش اطلاعات کاربر (ریپلای کن)
——————————————————————
⚠️ **فقط با ریپلای روی پیام هدف دستورها رو بزن!**
🩸 **#زامبی_نگهبان نسخه 1.1.0**
"""

def is_admin(user_id):
    return user_id in ADMINS

@bot.message_handler(commands=['help'])
def help_handler(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, help_text)

@bot.message_handler(commands=['adminn'])
def add_admin(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        ADMINS.add(message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ به مدیران اضافه شد.")

@bot.message_handler(commands=['dadminn'])
def del_admin(message):
    if message.reply_to_message and message.from_user.id == OWNER_ID:
        ADMINS.discard(message.reply_to_message.from_user.id)
        bot.reply_to(message, "⛔ از مدیران حذف شد.")

@bot.message_handler(commands=['hoi'])
def hoi(message):
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, hoi_reply)

@bot.message_handler(commands=['hosh'])
def hosh(message):
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, hosh_reply)

@bot.message_handler(commands=['ghanon'])
def ghanon(message):
    bot.reply_to(message, ghanon_text)

@bot.message_handler(commands=['mozahem'])
def add_mozahem(message):
    if message.reply_to_message:
        mozahem_users.add(message.reply_to_message.from_user.id)
        bot.reply_to(message, "❗ مزاحم شناسایی شد.")

@bot.message_handler(commands=['dmozahem'])
def remove_mozahem(message):
    if message.reply_to_message:
        mozahem_users.discard(message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ مزاحم حذف شد.")

@bot.message_handler(commands=['doshaman'])
def add_doshaman(message):
    if message.reply_to_message:
        doshaman_users.add(message.reply_to_message.from_user.id)
        bot.reply_to(message, "💣 دشمن فعال شد.")

@bot.message_handler(commands=['ddoshman'])
def remove_doshaman(message):
    if message.reply_to_message:
        doshaman_users.discard(message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ دشمن پاک شد.")

@bot.message_handler(commands=['bann'])
def bann(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        try:
            bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.reply_to(message, "⛔ کاربر بن شد.")
        except Exception:
            bot.reply_to(message, "❌ نتونستم بنش کنم.")

@bot.message_handler(commands=['mutee'])
def mutee(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        try:
            # سکوت دائمی بدون تایمر
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=False)
            bot.reply_to(message, "🔇 کاربر سکوت دائمی شد.")
        except Exception:
            bot.reply_to(message, "❌ خطا در سکوت.")

@bot.message_handler(commands=['unmutt'])
def unmutt(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        try:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=True)
            bot.reply_to(message, "🔊 سکوت برداشته شد.")
        except Exception:
            bot.reply_to(message, "❌ خطا در آزادسازی.")

@bot.message_handler(commands=['pinn'])
def pinn(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        try:
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
            bot.reply_to(message, "📌 پیام سنجاق شد.")
        except Exception:
            bot.reply_to(message, "❌ خطا در سنجاق.")

@bot.message_handler(commands=['unpin'])
def unpin(message):
    if is_admin(message.from_user.id):
        try:
            bot.unpin_chat_message(message.chat.id)
            bot.reply_to(message, "📍 سنجاق پاک شد.")
        except Exception:
            bot.reply_to(message, "❌ خطا در حذف سنجاق.")

# تگ کردن اعضای گروه
def tagging_thread():
    global tagging, tagged_message_ids, tag_text, tag_chat_id
    try:
        members = list(group_members)
        for user_id in members:
            if not tagging:
                break
            try:
                msg = bot.send_message(tag_chat_id, f"👤 [{user_id}](tg://user?id={user_id}) {tag_text}", parse_mode='Markdown')
                tagged_message_ids.append(msg.message_id)
                time.sleep(0.5)
            except Exception:
                continue
    except Exception:
        pass
    tagging = False

@bot.message_handler(commands=['tagg'])
def start_tag(message):
    global tagging, tag_text, tag_chat_id, tagged_message_ids, tag_thread
    if not is_admin(message.from_user.id):
        return
    if tagging:
        bot.reply_to(message, "⏳ در حال تگ کردن هستم، لطفا صبر کن یا /stopp بزن.")
        return
    tag_text = message.text[6:].strip()
    if not tag_text:
        tag_text = ""
    tag_chat_id = message.chat.id
    tagging = True
    tagged_message_ids = []
    tag_thread = threading.Thread(target=tagging_thread)
    tag_thread.start()
    bot.reply_to(message, "🏷 شروع تگ کردن اعضا...")

@bot.message_handler(commands=['stopp'])
def stop_tag(message):
    global tagging, tagged_message_ids, tag_chat_id
    if not is_admin(message.from_user.id):
        return
    tagging = False
    for msg_id in tagged_message_ids:
        try:
            bot.delete_message(tag_chat_id, msg_id)
        except Exception:
            pass
    tagged_message_ids = []
    bot.reply_to(message, "⏹️ تگ کردن متوقف و پیام‌ها حذف شدند.")

# ضد لینک
@bot.message_handler(commands=['zedlink'])
def enable_anti_link(message):
    if is_admin(message.from_user.id):
        anti_link_enabled.add(message.chat.id)
        bot.reply_to(message, "🔒 ضد لینک فعال شد؛ ارسال لینک پاک می‌شود.")

@bot.message_handler(commands=['dzedlink'])
def disable_anti_link(message):
    if is_admin(message.from_user.id):
        if message.chat.id in anti_link_enabled:
            anti_link_enabled.discard(message.chat.id)
        bot.reply_to(message, "🔓 ضد لینک غیرفعال شد.")

@bot.message_handler(commands=['ghofle'])
def lock_group(message):
    if is_admin(message.from_user.id):
        group_lock_enabled.add(message.chat.id)
        bot.reply_to(message, "🔒 گروه قفل شد؛ فقط مدیران می‌توانند پیام ارسال کنند.")

@bot.message_handler(commands=['dghofle'])
def unlock_group(message):
    if is_admin(message.from_user.id):
        if message.chat.id in group_lock_enabled:
            group_lock_enabled.discard(message.chat.id)
        bot.reply_to(message, "🔓 قفل گروه باز شد؛ همه می‌توانند پیام ارسال کنند.")

# حذف لینک در پیام‌ها و قفل گروه
@bot.message_handler(func=lambda message: True)
def check_links_and_locks(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.chat.id in anti_link_enabled:
            if message.text:
                if any(word in message.text.lower() for word in ['http://', 'https://', 't.me/', 'telegram.me/', 'www.']):
                    try:
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id, f"⚠️ لینک ممنوع است، {message.from_user.first_name} عزیز!", reply_to_message_id=message.message_id)
                        return
                    except Exception:
                        pass
        if message.chat.id in group_lock_enabled:
            if not is_admin(message.from_user.id):
                try:
                    bot.delete_message(message.chat.id, message.message_id)
                except Exception:
                    pass
                return
    uid = message.from_user.id
    if uid in mozahem_users:
        bot.reply_to(message, random.choice(mozahem_msgs))
    elif uid in doshaman_users:
        bot.reply_to(message, random.choice(doshaman_msgs))

# دستور /idd - نمایش اطلاعات کاربر
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

bot.infinity_polling()
