import telebot
import random

TOKEN = '8049022187:AAEoR_IorwWZ8KaH_UMvCo2fa1LjTqhnlWY'
OWNER_ID = 7341748124
bot = telebot.TeleBot(TOKEN)

# لیست مزاحمین و دشمنان
mozahem_users = set()
doshaman_users = set()

# پیام‌ها
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
⚔️ تابع باش... یا از این خاک محو شو.'''

mozahem_msgs = [
    "اوه اوه! باز داره مزاحمت می‌کنه، چرا اینقدر به خودت مطمئنی؟! 😂",
    "چی شد؟ باز حرف‌های تکراری؟ نکنه کم آوردی؟! 🙃",
    "هه! فکر کردی کسی گوش می‌کنه؟ بیشتر تلاش کن، هنوز راه داری! 😏",
    "این همه پیام می‌فرستی، انگار منتظر جایزه‌ای! 🏆",
    "مزاحمت مثل یک ویروس شده، باید واکسینه بشی! 🤒",
    "باز هم مزاحم شدی؟ داری جایزه‌ات رو می‌گیری! 🎉",
    "حرفات مثه صدای وزوز پشه‌ست، مزاحمی بی‌وقفه! 🦟",
    "آخه این همه پیام برای چی؟ دارم فکر می‌کنم برای کی می‌نویسی! 🤔",
    "تو مزاحم هستی و من تماشاگر، مسابقه‌ی پر سر و صدا! 🎭",
    "یه چیزی می‌گم، ولی بهتره فراموشش کنی! 😂",
    "زود باش، وقتشه که به اشتباهاتت پی ببری! ⏳",
    "اگه خسته شدی، به من بگو، من ادامه می‌دم! 😈",
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

@bot.message_handler(commands=['hoi'])
def handle_hoi(message):
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, hoi_reply_text)
    else:
        bot.reply_to(message, "دستور باید روی پیام شخص ریپلای بشه.")

@bot.message_handler(commands=['hosh'])
def handle_hosh(message):
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, hosh_reply_text)
    else:
        bot.reply_to(message, "دستور باید روی پیام شخص ریپلای بشه.")

@bot.message_handler(commands=['ghanon'])
def handle_ghanon(message):
    bot.reply_to(message, ghanon_text)

@bot.message_handler(commands=['mozahem'])
def handle_mozahem(message):
    if message.reply_to_message:
        uid = message.reply_to_message.from_user.id
        mozahem_users.add(uid)
        bot.reply_to(message, "✅ کاربر به لیست مزاحمین اضافه شد.")
    else:
        bot.reply_to(message, "دستور باید روی پیام فرد مزاحم ریپلای بشه.")

@bot.message_handler(commands=['dmozahem'])
def handle_dmozahem(message):
    if message.reply_to_message:
        uid = message.reply_to_message.from_user.id
        mozahem_users.discard(uid)
        bot.reply_to(message, "❎ کاربر از لیست مزاحمین حذف شد.")
    else:
        bot.reply_to(message, "دستور باید روی پیام فرد مزاحم ریپلای بشه.")

@bot.message_handler(commands=['doshaman'])
def handle_doshaman(message):
    if message.reply_to_message:
        uid = message.reply_to_message.from_user.id
        doshaman_users.add(uid)
        bot.reply_to(message, f"💥 دشمن شناسایی شد. عملیات تخریب علیه {uid} آغاز شد!")
    else:
        bot.reply_to(message, "دستور باید روی پیام دشمن ریپلای بشه.")

@bot.message_handler(commands=['ddoshman'])
def handle_ddoshman(message):
    if message.reply_to_message:
        uid = message.reply_to_message.from_user.id
        doshaman_users.discard(uid)
        bot.reply_to(message, f"🛑 دشمن {uid} از لیست حذف شد.")
    else:
        bot.reply_to(message, "دستور باید روی پیام دشمن ریپلای بشه.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    if message.from_user.id == OWNER_ID:
        help_text = '''«من یک زامبی نگهبانم؛ بی‌رحم، شکست‌ناپذیر و تا پای جان وفادار! از تو در برابر هر تهدیدی محافظت می‌کنم… و خط قرمزت برای دیگران، مرز مرگ است!» 🔪🩸  
  
[• هشدار و برخورد ⚠️🛡️]  
* /hoi – با ریپلای این دستور، به هدف هشدار اولیه داده میشه  
* /hosh – هشدار نهایی صادر میشه  
* /ghanon – ارسال قوانین رسمی گروه  
  
[• مدیریت مزاحمین 🛑]  
* /mozahem – اضافه‌کردن مزاحم  
* /dmozahem – حذف مزاحم  
  
[• دشمن‌یابی و تخریب 💥]  
* /doshaman – نابودی دشمن  
* /ddoshman – لغو تخریب  
'''
        bot.reply_to(message, help_text)
    else:
        bot.reply_to(message, "فقط مالک ربات به این دستور دسترسی داره.")

@bot.message_handler(func=lambda m: True)
def auto_react(message):
    uid = message.from_user.id
    if uid in mozahem_users:
        bot.reply_to(message, random.choice(mozahem_msgs))
    elif uid in doshaman_users:
        bot.reply_to(message, random.choice(doshaman_msgs))

bot.infinity_polling()
