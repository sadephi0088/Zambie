import telebot
import random

TOKEN = '8049022187:AAEoR_IorwWZ8KaH_UMvCo2fa1LjTqhnlWY'
OWNER_ID = 7341748124

bot = telebot.TeleBot(TOKEN)

# لیست مدیران ربات، اولش فقط خود مالک
admins = {OWNER_ID}

# ==========================
# پیام‌ها و متون دقیق از کاربر (بدون تغییر)
# ==========================

hoi_reply_text = '''#پیام_زامبی
نگاهت، رفتارت، حضورت... نسبت به اربابم.
همه زیر نظره من سنجیده میشه! مراقب قدم‌هایت باش.

موضوع: [تذکر، نگاه] 👁👁'''

hosh_reply_text = '''⚠️ هشدار نهایی از نگهبان زامبی!

تو داری به خط قرمز ارباب تجاوز میکنی...
لطفا ادامه نده این اخرین اخطاره...من است🩸🔪'''

ghanon_text = '''📜 قانون خون و سایه‌ها
(بیانیه‌ی رسمی زامبی نگهبان)

این مکان، قلمرو ارباب من و ساکنان اینجاست.
احترام، سکوت، و فرمان‌برداری از ادب... سه اصل مقدس در اینجاست.

✅ ورود هر عضو به این گروه، به‌معنای پذیرش کامل قوانین است:

1. بی‌احترامی به هم یا شوخی نابجا، خط قرمز ارباب من است.

2. هیچ‌کس بالاتر از قانون نیست؛ نه با قدرت، نه با کلمات.

3. مزاحمت، توهین، یا نگاه آلوده... با واکنش زامبی روبه‌رو خواهد شد.

4. هشدار، تنها یک بار صادر می‌شود؛ بعد از آن، حذف قطعی و برخورد خونین در انتظارت است.🌝

⚔️ تابع باش... یا از این خاک محو شو.
#بیانیه_زامبی [با اجازه از اربابم>]'''

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

doshaman_add_text = "کاربر {user} به لیست دشمنان اضافه شد.  \nزامبی آماده است تا با تمام قدرت علیه او عمل کند! 💥☠️"
doshaman_remove_text = "کاربر {user} از لیست دشمنان حذف شد."

mozahem_users = set()
doshaman_users = set()

# ==========================
# چک دسترسی مدیر
def is_admin(user_id):
    return user_id in admins

# ==========================
# فرمان‌ها
# ==========================

@bot.message_handler(commands=['hoi'])
def cmd_hoi(message):
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, hoi_reply_text)
    else:
        bot.reply_to(message, "لطفاً این دستور را روی پیام هدف ریپلای کنید.")

@bot.message_handler(commands=['hosh'])
def cmd_hosh(message):
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, hosh_reply_text)
    else:
        bot.reply_to(message, "لطفاً این دستور را روی پیام هدف ریپلای کنید.")

@bot.message_handler(commands=['ghanon'])
def cmd_ghanon(message):
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, ghanon_text)
    else:
        bot.reply_to(message, ghanon_text)

@bot.message_handler(commands=['mozahem'])
def cmd_mozahem(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        mozahem_users.add(user_id)
        bot.reply_to(message, f"کاربر {user_id} به لیست مزاحمین اضافه شد.")
    else:
        bot.reply_to(message, "لطفاً این دستور را روی پیام فرد مزاحم ریپلای کنید.")

@bot.message_handler(commands=['dmozahem'])
def cmd_dmozahem(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        if user_id in mozahem_users:
            mozahem_users.remove(user_id)
            bot.reply_to(message, f"کاربر {user_id} از لیست مزاحمین حذف شد.")
        else:
            bot.reply_to(message, "این کاربر در لیست مزاحمین نیست.")
    else:
        bot.reply_to(message, "لطفاً این دستور را روی پیام فرد مزاحم ریپلای کنید.")

@bot.message_handler(commands=['doshaman'])
def cmd_doshaman(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        doshaman_users.add(user_id)
        user_name = (message.reply_to_message.from_user.username or
                     message.reply_to_message.from_user.first_name or
                     str(user_id))
        bot.reply_to(message, doshaman_add_text.format(user=user_name))
    else:
        bot.reply_to(message, "لطفاً این دستور را روی پیام هدف ریپلای کنید.")

@bot.message_handler(commands=['ddoshman'])
def cmd_ddoshman(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        if user_id in doshaman_users:
            doshaman_users.remove(user_id)
            user_name = (message.reply_to_message.from_user.username or
                         message.reply_to_message.from_user.first_name or
                         str(user_id))
            bot.reply_to(message, doshaman_remove_text.format(user=user_name))
        else:
            bot.reply_to(message, "این کاربر در لیست دشمنان نیست.")
    else:
        bot.reply_to(message, "لطفاً این دستور را روی پیام هدف ریپلای کنید.")

# ==========================
# دستورات بن، سکوت، لغو سکوت و مدیریت ادمین‌ها

# بن کردن کاربر (فقط مدیرها)
@bot.message_handler(commands=['bann'])
def cmd_bann(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "شما اجازه دسترسی به این دستور را ندارید.")
        return
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id
        try:
            bot.kick_chat_member(chat_id, user_id)
            bot.reply_to(message, f"کاربر {user_id} بن شد.")
        except Exception as e:
            bot.reply_to(message, f"خطا در بن کردن: {e}")
    else:
        bot.reply_to(message, "لطفاً این دستور را روی پیام فرد مورد نظر ریپلای کنید.")

# سکوت کردن کاربر (محدود کردن ارسال پیام)
@bot.message_handler(commands=['mutee'])
def cmd_mutee(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "شما اجازه دسترسی به این دستور را ندارید.")
        return
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id
        try:
            bot.restrict_chat_member(
                chat_id, user_id,
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
            bot.reply_to(message, f"کاربر {user_id} سکوت شد.")
        except Exception as e:
            bot.reply_to(message, f"خطا در سکوت کردن: {e}")
    else:
        bot.reply_to(message, "لطفاً این دستور را روی پیام فرد مورد نظر ریپلای کنید.")

# لغو سکوت کاربر
@bot.message_handler(commands=['unmutt'])
def cmd_unmutt(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "شما اجازه دسترسی به این دستور را ندارید.")
        return
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id
        try:
            bot.restrict_chat_member(
                chat_id, user_id,
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            bot.reply_to(message, f"کاربر {user_id} از سکوت خارج شد.")
        except Exception as e:
            bot.reply_to(message, f"خطا در لغو سکوت: {e}")
    else:
        bot.reply_to(message, "لطفاً این دستور را روی پیام فرد مورد نظر ریپلای کنید.")

# افزودن مدیر جدید به ربات (دسترسی کامل)
@bot.message_handler(commands=['adminn'])
def cmd_adminn(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "شما اجازه دسترسی به این دستور را ندارید.")
        return
    if message.reply_to_message:
        new_admin_id = message.reply_to_message.from_user.id
        admins.add(new_admin_id)
        bot.reply_to(message, f"کاربر {new_admin_id} به مدیران ربات اضافه شد.")
    else:
        bot.reply_to(message, "لطفاً این دستور را روی پیام فردی که می‌خواهید مدیر کنید ریپلای کنید.")

# حذف مدیر از ربات
@bot.message_handler(commands=['dadminn'])
def cmd_dadminn(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "شما اجازه دسترسی به این دستور را ندارید.")
        return
    if message.reply_to_message:
        rem_admin_id = message.reply_to_message.from_user.id
        if rem_admin_id == OWNER_ID:
            bot.reply_to(message, "مالک ربات را نمی‌توان حذف کرد.")
            return
        if rem_admin_id in admins:
            admins.remove(rem_admin_id)
            bot.reply_to(message, f"کاربر {rem_admin_id} از مدیران ربات حذف شد.")
        else:
            bot.reply_to(message, "این کاربر مدیر نیست.")
    else:
        bot.reply_to(message, "لطفاً این دستور را روی پیام فردی که می‌خواهید حذف کنید ریپلای کنید.")

# ==========================
# پاسخ به پیام‌های کاربران مزاحم و دشمنان
# ==========================

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    user_id = message.from_user.id
    if user_id in mozahem_users:
        reply_text = random.choice(mozahem_msgs)
        bot.reply_to(message, reply_text)
        return
    if user_id in doshaman_users:
        reply_text = random.choice(doshaman_msgs)
        bot.reply_to(message, reply_text)
        return

# ==========================
# راهنمای ربات (/help)
# ==========================

@bot.message_handler(commands=['help'])
def cmd_help(message):
    if message.from_user.id == OWNER_ID:
        help_text = '''⚔ 《 راهنما زامبی-محافظت از شما 》 ⚔
——————————————————————

🔰 هشدارها:
  /hoi     ▶ هشدار اولیه (ریپلای کن)
  /hosh    ▶ اخطار نهایی (ریپلای کن)
  /ghanon  ▶ لزوم رعایت قانون

——————————————————————

😈 واکنش به مزاحمین:
  /mozahem   ▶ مزاحم شد (ریپلای کن)
  /dmozahem  ▶ حذف مزاحم (ریپلای کن)

——————————————————————

💀 نابود کردن دشمنان:
  /doshaman  ▶ حمله به دشمن (ریپلای کن)
  /ddoshman  ▶ لغو حمله (ریپلای کن)
  /bann      ▶ بن کردن کاربر (ریپلای کن)
  /mutee     ▶ سکوت کردن کاربر (ریپلای کن)
  /unmutt    ▶ لغو سکوت (ریپلای کن)

——————————————————————

⚠️ فقط با ریپلای روی پیام هدف دستورها رو بزن!

🩸 #زامبی_نگهبان نسخه 1.1.0
'''
        bot.reply_to(message, help_text)
    else:
        bot.reply_to(message, "شما اجازه دسترسی به این دستور را ندارید.")

# ==========================
# اجرای ربات
# ==========================

bot.infinity_polling()
