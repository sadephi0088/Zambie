import telebot
import random

TOKEN = '8049022187:AAEoR_IorwWZ8KaH_UMvCo2fa1LjTqhnlWY'
OWNER_ID = 7341748124
ADMINS = {OWNER_ID}

bot = telebot.TeleBot(TOKEN)

mozahem_users = set()
doshaman_users = set()

# پیام‌های ثابت
hoi_reply = "👁‍🗨 **نگاهت، رفتارت، حضورت... تحت نظرمه! مراقب باش.**"
hosh_reply = "⚠️ **آخرین اخطار! ادامه بدی... حمله می‌کنم!**"
ghanon_text = "📜 **قانون خون و سایه‌ها رو رعایت کن یا از بین می‌ری!**"

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
  /mutee     ▶ سکوت ۱ دقیقه‌ای (ریپلای کن)
  /unmutt    ▶ لغو سکوت (ریپلای کن)
——————————————————————
📌 **سنجاق پیام‌ها:**
  /pinn      ▶ سنجاق پیام (ریپلای کن)
  /unpin     ▶ حذف سنجاق (ریپلای کن)
——————————————————————
⚙️ **مدیریت:**
  /adminn    ▶ ارتقای فرد به مدیر ربات (ریپلای کن)
  /dadminn   ▶ حذف فرد از مدیریت (ریپلای کن)
——————————————————————
⚠️ **فقط با ریپلای روی پیام هدف دستورها رو بزن!**
🩸 **#زامبی_نگهبان نسخه 1.1.0**"""

# دستورات
@bot.message_handler(commands=['help'])
def help_handler(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, help_text)

def is_admin(uid):
    return uid in ADMINS

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
        except:
            bot.reply_to(message, "❌ نتونستم بنش کنم.")

@bot.message_handler(commands=['mutee'])
def mutee(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        try:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=60, can_send_messages=False)
            bot.reply_to(message, "🔇 کاربر ساکت شد.")
        except:
            bot.reply_to(message, "❌ خطا در سکوت.")

@bot.message_handler(commands=['unmutt'])
def unmutt(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        try:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=True)
            bot.reply_to(message, "🔊 سکوت برداشته شد.")
        except:
            bot.reply_to(message, "❌ خطا در آزادسازی.")

@bot.message_handler(commands=['pinn'])
def pinn(message):
    if message.reply_to_message and is_admin(message.from_user.id):
        try:
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
            bot.reply_to(message, "📌 پیام سنجاق شد.")
        except:
            bot.reply_to(message, "❌ خطا در سنجاق.")

@bot.message_handler(commands=['unpin'])
def unpin(message):
    if is_admin(message.from_user.id):
        try:
            bot.unpin_chat_message(message.chat.id)
            bot.reply_to(message, "📍 سنجاق پاک شد.")
        except:
            bot.reply_to(message, "❌ خطا در حذف سنجاق.")

@bot.message_handler(func=lambda m: True)
def reply_random(message):
    uid = message.from_user.id
    if uid in mozahem_users:
        bot.reply_to(message, random.choice(mozahem_msgs))
    elif uid in doshaman_users:
        bot.reply_to(message, random.choice(doshaman_msgs))

bot.infinity_polling()
