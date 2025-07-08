import sqlite3
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
bot = TeleBot(TOKEN)

conn = sqlite3.connect('tiktak.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT,
    username TEXT,
    nickname TEXT DEFAULT '',
    coins INTEGER DEFAULT 300,
    gems INTEGER DEFAULT 15,
    form_type TEXT DEFAULT 'pro',
    birthdate TEXT DEFAULT '',
    hashtag TEXT DEFAULT '',
    slogan TEXT DEFAULT '',
    rank TEXT DEFAULT '',
    title TEXT DEFAULT ''
)
''')
conn.commit()

# پیام خوش آمدگویی
def welcome_text(full_name, user_id, username):
    return f"""╔═━⊱🌟 TikTak • پیام ورود 🌟⊰━═╗  
🎉 به امپراطوری تیک‌تاک خوش‌آمدی {full_name} عزیز!💢
🆔 آیدی: {user_id}  
🔗 یوزرنیم: {('@' + username) if username else 'ندارد ❌'}
━━━━━━━━━━━━━━━━━━  

📄 پروفایل اختصاصی‌ت ساخته شد!  
🎭 قدرت‌هات، افتخاراتت، امتیازاتت... همه اینجاست!
👁‍🗨 برای دیدنش، فقط توی گروه بنویس:  
/mee   👈
━━━━━━━━━━━━━━━━━━  
🌟 با عشق، تیم مدیریت TikTak Master"""

# فرم حرفه ای (عمومی)
def form_pro(user):
    return f"""🌟━━━【 🛡️ فرم حرفه‌ای - PRO 】━━━🌟

👤 نام: {user['full_name']}
✨ یوزرنیم شما: @{user['username'] if user['username'] else 'ندارد'}
🏷️ لقب اختصاصی: {user['nickname']}

• دارایی شما: •
💰 سکه: {user['coins']}
💎 الماس: {user['gems']}
⚜️ نشان طلایی: [ فرم عادی -PRO ]

🔮 قدرت‌ها و طلسم‌ها:
🎂 تاریخ تولد: {user['birthdate']}
♨️ هشتگ اختصاصی: {user['hashtag']}
⚔️ شعار شما: {user['slogan']}

⚡️ درجه‌ی شما: {user['rank']}
💰 مقام شما: {user['title']}

💼 این فقط شروع راه شماست…
🌟 با تلاش، می‌تونی به فرم‌های بالاتر دست پیدا کنی!"""

# فرم طلایی
def form_gold(user):
    return f"""🌟━━━【 👑 فرم طلایی - GOLD 】━━━🌟

👑 نام: {user['full_name']} 👑  
✨ یوزرنیم شما: @{user['username'] if user['username'] else 'ندارد'}  
🏷️ لقب اختصاصی: {user['nickname']}  

💼 دارایی طلایی شما:  
💰 سکه: {user['coins']}  
💎 الماس: {user['gems']}  
⚜️ نشان طلایی: [فرم طلایی - Gold]

🔮 قدرت‌ها و طلسم‌های ویژه:  
🎂 تاریخ تولد: {user['birthdate']}  
♨️ هشتگ اختصاصی: {user['hashtag']}  
⚔️ شعار شما: {user['slogan']}  

⚡️ درجه‌ی شما: {user['rank']}  
💰 مقام شما: {user['title']}  

🌟 به سطح طلایی خوش آمدید!  
✨ مسیر شما به سوی جاودانگی روشن است..."""

# فرم پلاس
def form_plus(user):
    return f"""🌌 تنها برای جاودانه‌ترین فرمانروایان TikTak 🌌

🌟━━━━━━【 👑 فرم پلاس - PLUS ∞ 】━━━━━━🌟

👑 نام: {user['full_name']} 👑
✨ یوزرنیم شما: @{user['username'] if user['username'] else 'ندارد'}
🏷️ لقب اختصاصی:
━━━━━━━━━━━━
💼 دارایی فوق‌العاده شما:
💰 سکه: {user['coins']}
💎 الماس: {user['gems']}
⚜️ نشان طلایی: ✔ فعال
━━━━━━━━━━━━
🔮 قدرت‌ها و طلسم‌های ویژه:
🎂 تاریخ تولد: {user['birthdate']}
♨️ هشتگ اختصاصی: {user['hashtag']}
⚔️ دسترسی به طلسم‌های ممنوعه
━━━━━━━━━━━━
🧿 درجه‌ی شما:
👑 امپراطور جاودانه
💰 مقام شما: {user['title']}
━━━━━━━━━━━━
🌟 فقط یک نفر شایسته‌ی این فرم خواهد بود...
🪄 فرم پلاس ∞، قدرتی فراتر از تصور 🌌"""

# کیبوردهای اینلاین

def main_profile_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🛒 فروشگاه قدرت‌ها", callback_data="open_shop"),
        InlineKeyboardButton("📘 راهنمای استفاده", callback_data="open_help")
    )
    return keyboard

def shop_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.row(
        InlineKeyboardButton("🛡️ خرید قدرت‌ها", callback_data="buy_powers"),
        InlineKeyboardButton("🎯 تجهیزات شخصی", callback_data="personal_items")
    )
    keyboard.add(
        InlineKeyboardButton("💟 خرید فرم [سطح بالاتر]", callback_data="buy_form")
    )
    keyboard.add(
        InlineKeyboardButton("↩️ بازگشت", callback_data="back_to_profile")
    )
    return keyboard

def form_buy_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🟡 خرید فرم طلایی (Gold)", callback_data="buy_gold_form"),
        InlineKeyboardButton("👑 خرید فرم فرمانروایان (Plus)", callback_data="buy_plus_form")
    )
    keyboard.add(
        InlineKeyboardButton("↩️ بازگشت", callback_data="back_to_shop")
    )
    return keyboard

# هندلر شروع

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username or ''

    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, full_name, username) VALUES (?, ?, ?)",
                       (user_id, full_name, username))
        conn.commit()
    bot.send_message(message.chat.id, welcome_text(full_name, user_id, username))

# هندلر پنل /mee

@bot.message_handler(commands=['mee'])
def mee_handler(message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        bot.send_message(message.chat.id, "❌ شما در سیستم ثبت نشده‌اید. لطفاً /start را بزنید.")
        return

    user = {
        'user_id': row[0],
        'full_name': row[1],
        'username': row[2],
        'nickname': row[3],
        'coins': row[4],
        'gems': row[5],
        'form_type': row[6],
        'birthdate': row[7],
        'hashtag': row[8],
        'slogan': row[9],
        'rank': row[10],
        'title': row[11]
    }

    if user['form_type'] == 'pro':
        text = form_pro(user)
    elif user['form_type'] == 'gold':
        text = form_gold(user)
    elif user['form_type'] == 'plus':
        text = form_plus(user)
    else:
        text = form_pro(user)

    bot.send_message(message.chat.id, text, reply_markup=main_profile_keyboard())

# هندلر باز کردن فروشگاه

@bot.callback_query_handler(func=lambda call: call.data == "open_shop")
def open_shop_handler(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="""🎉 به فروشگاه رسمی امپراطوری TikTak خوش اومدی!

اینجا سرزمین قدرت و افتخاره...  
جایی که می‌تونی فرم (قالب استعلام پروفایلت) رو ارتقا بدی،  
قدرت‌های خاص بخری، و تجهیزات منحصر‌به‌فرد مثل:  
📛 لقب اختصاصی  
🎂 تاریخ تولد  
♨️ هشتگ شخصی  
⚔️ طلسم‌های ممنوعه و خیلی بیشتر...""",
        reply_markup=shop_keyboard()
    )

# بازگشت به پروفایل

@bot.callback_query_handler(func=lambda call: call.data == "back_to_profile")
def back_to_profile_handler(call):
    user_id = call.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        bot.answer_callback_query(call.id, "❌ خطا در بازیابی اطلاعات.")
        return
    user = {
        'user_id': row[0],
        'full_name': row[1],
        'username': row[2],
        'nickname': row[3],
        'coins': row[4],
        'gems': row[5],
        'form_type': row[6],
        'birthdate': row[7],
        'hashtag': row[8],
        'slogan': row[9],
        'rank': row[10],
        'title': row[11]
    }
    if user['form_type'] == 'pro':
        text = form_pro(user)
    elif user['form_type'] == 'gold':
        text = form_gold(user)
    elif user['form_type'] == 'plus':
        text = form_plus(user)
    else:
        text = form_pro(user)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=text,
                          reply_markup=main_profile_keyboard())

# بازگشت به فروشگاه

@bot.callback_query_handler(func=lambda call: call.data == "back_to_shop")
def back_to_shop_handler(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="""🎉 به فروشگاه رسمی امپراطوری TikTak خوش اومدی!

اینجا سرزمین قدرت و افتخاره...  
جایی که می‌تونی فرم (قالب استعلام پروفایلت) رو ارتقا بدی،  
قدرت‌های خاص بخری، و تجهیزات منحصر‌به‌فرد مثل:  
📛 لقب اختصاصی  
🎂 تاریخ تولد  
♨️ هشتگ شخصی  
⚔️ طلسم‌های ممنوعه و خیلی بیشتر...""",
        reply_markup=shop_keyboard()
    )

# باز کردن صفحه خرید فرم

@bot.callback_query_handler(func=lambda call: call.data == "buy_form")
def buy_form_handler(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="""🌟 انتخاب کن که کدوم فرم سلطنتی رو می‌خوای! 🌟

💟 فرم طلایی - GOLD  
✨ ظاهر شیک و امکانات ویژه برای فرمانروایان با ذوق

👑 فرم فرمانروایان - PLUS  
♾️ قدرت‌های فراتر از تصور برای پادشاهان جاودانه

کدوم یکی رو می‌خوای بخری؟""",
        reply_markup=form_buy_keyboard()
    )

# خرید فرم طلایی

@bot.callback_query_handler(func=lambda call: call.data == "buy_gold_form")
def buy_gold_form_handler(call):
    user_id = call.from_user.id
    cursor.execute("SELECT gems FROM users WHERE user_id=?", (user_id,))
    gems = cursor.fetchone()[0]

    cost = 10
    if gems < cost:
        bot.answer_callback_query(call.id, "❌ الماس کافی نیست!")
        return

    # کم کردن الماس و تغییر فرم
    cursor.execute("UPDATE users SET gems = gems - ?, form_type = 'gold' WHERE user_id=?", (cost, user_id))
    conn.commit()

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🌟 خرید موفق! شما اکنون فرم طلایی را دارید. مدت اعتبار: یک هفته. پس از اتمام اعتبار، فرم شما به پرو باز می‌گردد."
    )

# خرید فرم پلاس

@bot.callback_query_handler(func=lambda call: call.data == "buy_plus_form")
def buy_plus_form_handler(call):
    user_id = call.from_user.id
    cursor.execute("SELECT gems FROM users WHERE user_id=?", (user_id,))
    gems = cursor.fetchone()[0]

    cost = 200
    if gems < cost:
        bot.answer_callback_query(call.id, "❌ الماس کافی نیست!")
        return

    cursor.execute("UPDATE users SET gems = gems - ?, form_type = 'plus' WHERE user_id=?", (cost, user_id))
    conn.commit()

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🌟 خرید موفق! شما اکنون فرم فرمانروایان (Plus) را دارید. مدت اعتبار: یک ماه. پس از اتمام اعتبار، فرم شما به پرو باز می‌گردد."
    )

# هندلر راهنما (مثال)

@bot.callback_query_handler(func=lambda call: call.data == "open_help")
def open_help_handler(call):
    help_text = """📘 راهنمای استفاده از ربات TikTak:

- /mee : نمایش پروفایل شما  
- فروشگاه قدرت‌ها: خرید قدرت و تجهیزات  
- خرید فرم‌ها: ارتقا به فرم‌های طلایی و فرمانروایان  
- برای اطلاعات بیشتر به ادمین مراجعه کنید."""
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, help_text)

# توابع بیشتر و توسعه دلخواه می‌تونی اضافه کنی...

# اجرای ربات
bot.infinity_polling()
