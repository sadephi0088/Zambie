import os
import time
import threading
import re
import sqlite3
from datetime import datetime
from flask import Flask
import telebot
from telebot import types

# —————————————————————————————————————————————
# Configuration
TOKEN     = "7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs"
OWNER_ID  = 7341748124
bot       = telebot.TeleBot(TOKEN)
bot.remove_webhook()
time.sleep(1)

# Simple Flask server for cron-job pings
app = Flask(__name__)
@app.route("/")
def ping():
    return "OK"
threading.Thread(
    target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000))),
    daemon=True
).start()

# —————————————————————————————————————————————
# Database connections
conn        = sqlite3.connect("data.db", check_same_thread=False)
conn_thread = sqlite3.connect("data.db", check_same_thread=False)

def init_db(cxn):
    cur = cxn.cursor()
    # users table
    cur.execute('''
      CREATE TABLE IF NOT EXISTS users (
        user_id      INTEGER PRIMARY KEY,
        name         TEXT,
        username     TEXT,
        coin         INTEGER DEFAULT 180,
        score        INTEGER DEFAULT 250,
        gold_tick    INTEGER DEFAULT 0,
        role         TEXT DEFAULT 'ممبر عادی 🧍',
        birthdate    TEXT,
        partner_id   INTEGER,
        child_of     INTEGER,
        pet          TEXT,
        custom_emoji TEXT,
        sect         TEXT,
        messages     INTEGER DEFAULT 0,
        is_admin     INTEGER DEFAULT 0,
        is_blocked   INTEGER DEFAULT 0
      )
    ''')
    # sects table
    cur.execute('''
      CREATE TABLE IF NOT EXISTS sects (
        name      TEXT PRIMARY KEY,
        owner_id  INTEGER
      )
    ''')
    cxn.commit()

init_db(conn)
init_db(conn_thread)

# —————————————————————————————————————————————
# Rank dictionary
ranks = {
  "m1":"سوگولی گروه 💋"
  "m2":"پرنسس گروه 👑"
  "m3":"ملکه گروه 👸"
  "m4":"شوالیه گروه 🛡️"
  "m5":"رهبر گروه 🦁"
  "m6":"اونر گروه 🌀",
  "m7":"زامبی الفا گروه 🧟‍♂️"
  "m8":"نفس گروه 💨"
  "m9":"بادیگارد گروه 🕶️"
  "m10":"ممبر عادی 🧍"
  "m11":"عاشق دلباخته ❤️‍🔥"
  "m12":"برده گروه 🧎",
  "m13":"رئیس گروه 🧠"
  "m14":"کصشرگوی گروه 🐵"
  "m15":"دختر شاه 👑👧"
}

# Pending requests memory
pending_loves         = {}
pending_children      = {}
pending_sect_invites  = {}
sect_ranking_cache    = []

# —————————————————————————————————————————————
# Helper functions
def add_user(uid, name, uname):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE user_id=?", (uid,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users(user_id,name,username) VALUES(?,?,?)",
                    (uid,name,uname))
        conn.commit()

def get_username(uid):
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    return r[0] if r and r[0] else "ندارد ❌"

def get_rank(score):
    if score < 500:   return "تازه‌کار 👶"
    if score < 1000:  return "حرفه‌ای 🔥"
    if score < 2000:  return "استاد 🌟"
    if score < 4000:  return "قهرمان 🏆"
    if score < 7000:  return "افسانه‌ای 🐉"
    if score < 10000: return "بی‌نظیر 💎"
    return "اسطوره 🚀"

def is_admin(uid):
    if uid == OWNER_ID: return True
    cur = conn.cursor()
    cur.execute("SELECT is_admin FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    return bool(r and r[0] == 1)

def check_blocked(uid):
    cur = conn.cursor()
    cur.execute("SELECT is_blocked FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    return bool(r and r[0] == 1)

def check_gold_tick(uid):
    cur = conn.cursor()
    cur.execute("SELECT score,gold_tick FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    if r and r[0] >= 5000 and r[1] == 0:
        cur.execute("UPDATE users SET gold_tick=1 WHERE user_id=?", (uid,))
        conn.commit()

def blocked_guard(f):
    def wrapper(m):
        add_user(m.from_user.id, m.from_user.first_name, m.from_user.username or "ندارد")
        if check_blocked(m.from_user.id):
            bot.reply_to(m, "❌ حساب شما در حالت تعلیق است!")
            return
        return f(m)
    return wrapper

# —————————————————————————————————————————————
# Update sect ranking periodically
def update_sects():
    cur = conn_thread.cursor()
    global sect_ranking_cache
    while True:
        cur.execute(
          "SELECT sect,COUNT(*) cnt FROM users "
          "WHERE sect IS NOT NULL GROUP BY sect "
          "ORDER BY cnt DESC LIMIT 10"
        )
        sect_ranking_cache = cur.fetchall()
        time.sleep(3600)

threading.Thread(target=update_sects, daemon=True).start()

# —————————————————————————————————————————————
# Protect: only OWNER can add bot to groups
@bot.my_chat_member_handler()
def on_bot_added(msg):
    if msg.new_chat_member.status in ("member","administrator"):
        adder = msg.from_user.id
        if adder != OWNER_ID:
            try:
                bot.send_message(msg.chat.id,
                  "❌ تنها مالک ربات می‌تواند مرا به گروه اضافه کند.")
                bot.leave_chat(msg.chat.id)
            except:
                pass

# —————————————————————————————————————————————
# START / HELP / RANKS
@bot.message_handler(commands=['start'])
@blocked_guard
def cmd_start(m):
    txt = f'''
سلام @{m.from_user.username}! 🌹
دستورات:
/my /love /dlove /give
/pet /unpet /child /dchild
/emoji /reemoji
/sectcreate /sectinvite /sectleave
/sectdisband /dferghe
/rank /mee /block /dblock
/admin /dadmin /ddadmin
/shop /del /mut
'''
    bot.reply_to(m, txt)

@bot.message_handler(commands=['help'])
@blocked_guard
def cmd_help(m):
    bot.reply_to(m, "🔰 برای لیست کامل /start را ارسال کنید")

@bot.message_handler(commands=['ranks'])
@blocked_guard
def cmd_ranks(m):
    txt = "📜 مقام‌های ربات:\n" + "\n".join(f"{k} — {v}" for k,v in ranks.items())
    bot.reply_to(m, txt)

# —————————————————————————————————————————————
# PROFILE / OLD
@bot.message_handler(commands=['my'])
@blocked_guard
def cmd_my(m):
    target = m.reply_to_message.from_user.id if m.reply_to_message and is_admin(m.from_user.id) else m.from_user.id
    add_user(target,
             m.reply_to_message.from_user.first_name if m.reply_to_message else m.from_user.first_name,
             get_username(target))
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (target,))
    d = cur.fetchone()
    if not d:
        return bot.reply_to(m, "❌ خطا در بازیابی پروفایل.")
    cur.execute("SELECT username FROM users WHERE child_of=?", (target,))
    children = [f"@{r[0]}" for r in cur.fetchall()]
    text = f'''
━━━【 پروفایل شما در گروه 】━━━

•مشخصات فردی شما•
👤 نام: {d[1]}
✨ یوزرنیم: @{d[2]}
⚔️ آیدی: {d[0]}

🌐 کشور: 🇮🇷 ایران

•• دارایی و امتیاز: ••
💰 سکه: {d[3]}
💎 امتیاز: {d[4]}
⚜️ تیک طلایی: {"دارد ✅" if d[5]==1 else "ندارد ❌"}

•خانواده و علایق:•
😍 همسر: {get_username(d[8])}
👶 فرزندان: {', '.join(children) or 'ندارد ❌'}
🐾 پت: {d[10] or 'ندارد ❌'}
🏷️ فرقه: {d[12] or 'ندارد ❌'}
🎭 ایموجی: {d[11] or 'ندارد ❌'}
🎂 تولد: {d[7] or 'ثبت نشده ❌'}

:: در گروه ::
🏆 درجه: {get_rank(d[4])}
💠 مقام: {d[6]}
'''
    bot.reply_to(m, text)

@bot.message_handler(commands=['old'])
@blocked_guard
def cmd_old(m):
    mt = re.match(r'^/old (\d{4}/\d{1,2}/\d{1,2})$', m.text.strip())
    if not mt:
        return bot.reply_to(m, "❌ فرمت: /old YYYY/M/D")
    bd,uid = mt.group(1), m.from_user.id
    cur = conn.cursor()
    cur.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if cur.fetchone()[0] < 40:
        return bot.reply_to(m, "❌ سکه کافی نیست!")
    cur.execute("UPDATE users SET birthdate=?,coin=coin-40 WHERE user_id=?", (bd,uid))
    conn.commit()
    bot.reply_to(m, "🎂 تولد ثبت شد و ۴۰ سکه کسر گردید.")

# —————————————————————————————————————————————
# LOVE & DIVORCE
@bot.message_handler(commands=['love'])
@blocked_guard
def cmd_love(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "❌ ریپلای کنید.")
    rid,sid = m.from_user.id, m.reply_to_message.from_user.id
    if rid==sid:
        return bot.reply_to(m, "❌ غیرمعتبر!")
    add_user(rid, m.from_user.first_name, m.from_user.username or "")
    add_user(sid, m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.username or "")
    kb = types.InlineKeyboardMarkup()
    kb.add(
      types.InlineKeyboardButton("💖 قبول", callback_data=f"accept_{rid}"),
      types.InlineKeyboardButton("💔 رد"  , callback_data=f"reject_{rid}")
    )
    sent = bot.send_message(m.chat.id,
      f"💌 @{m.from_user.username} عاشق @{m.reply_to_message.from_user.username} شد!\nقبول می‌کنی؟",
      reply_markup=kb
    )
    pending_loves[sent.message_id] = rid

@bot.callback_query_handler(lambda c: c.data.startswith(("accept_","reject_")))
def cb_love(ca):
    mid = ca.message.message_id
    if mid not in pending_loves:
        return bot.answer_callback_query(ca.id, "❌ منقضی شد.")
    rid,sid = pending_loves[mid], ca.from_user.id
    cur = conn.cursor()
    if ca.data.startswith("accept_"):
        cur.execute("SELECT coin FROM users WHERE user_id=?", (rid,))
        if cur.fetchone()[0] < 40:
            bot.edit_message_text("❌ سکه کافی نیست!", ca.message.chat.id, mid)
            del pending_loves[mid]; return
        cur.execute("UPDATE users SET partner_id=?,coin=coin-40 WHERE user_id=?", (sid,rid))
        cur.execute("UPDATE users SET partner_id=? WHERE user_id=?", (rid,sid))
        conn.commit()
        bot.edit_message_text("💒 ازدواج ثبت شد! 🎉", ca.message.chat.id, mid)
        bot.send_message(ca.message.chat.id, f"🎊 @{get_username(rid)} و @{get_username(sid)} زوج شدند!")
    else:
        bot.edit_message_text("💔 رد شد.", ca.message.chat.id, mid)
    del pending_loves[mid]

@bot.message_handler(commands=['dlove'])
@blocked_guard
def cmd_dlove(m):
    uid = m.from_user.id
    cur = conn.cursor()
    cur.execute("SELECT partner_id FROM users WHERE user_id=?", (uid,))
    row = cur.fetchone()
    if not row or not row[0]:
        return bot.reply_to(m, "❌ رابطه‌ای ندارید.")
    pid = row[0]
    cur.execute("UPDATE users SET partner_id=NULL WHERE user_id IN(?,?)", (uid,pid))
    conn.commit()
    bot.send_message(m.chat.id, f"💔 @{get_username(uid)} و @{get_username(pid)} جدا شدند.")

# —————————————————————————————————————————————
# PET SYSTEM
@bot.message_handler(commands=['pet'])
@blocked_guard
def cmd_pet(m):
    parts = m.text.strip().split(maxsplit=1)
    if len(parts)!=2:
        return bot.reply_to(m, "❌ /pet نام‌حیوان")
    pet,uid = parts[1], m.from_user.id
    cur  = conn.cursor()
    cur.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if cur.fetchone()[0]<40:
        return bot.reply_to(m, "❌ سکه کافی نیست!")
    cur.execute("UPDATE users SET pet=?,coin=coin-40 WHERE user_id=?", (pet,uid))
    conn.commit()
    bot.reply_to(m, f"🐾 `{pet}` ثبت شد! -40 سکه", parse_mode="Markdown")

@bot.message_handler(commands=['unpet'])
@blocked_guard
def cmd_unpet(m):
    uid = m.from_user.id
    cur = conn.cursor()
    cur.execute("SELECT pet FROM users WHERE user_id=?", (uid,))
    if not cur.fetchone()[0]:
        return bot.reply_to(m, "❌ ندارید!")
    cur.execute("UPDATE users SET pet=NULL WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m, "🐾 پت حذف شد.")

# —————————————————————————————————————————————
# CHILD SYSTEM
@bot.message_handler(commands=['child'])
@blocked_guard
def cmd_child(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "❌ ریپلای کنید.")
    rid,sid = m.from_user.id, m.reply_to_message.from_user.id
    if rid==sid:
        return bot.reply_to(m, "❌ غیرمعتبر!")
    add_user(rid, m.from_user.first_name, m.from_user.username or "")
    add_user(sid, m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.username or "")
    kb = types.InlineKeyboardMarkup()
    kb.add(
      types.InlineKeyboardButton("👶 قبول", callback_data=f"caccept_{rid}"),
      types.InlineKeyboardButton("❌ رد"  , callback_data=f"creject_{rid}")
    )
    sent = bot.send_message(m.chat.id,
      f"👶 @{m.from_user.username} درخواست فرزند @{m.reply_to_message.from_user.username} داد!\nقبول؟",
      reply_markup=kb
    )
    pending_children[sent.message_id] = rid

@bot.callback_query_handler(lambda c: c.data.startswith(("caccept_","creject_")))
def cb_child(ca):
    mid = ca.message.message_id
    if mid not in pending_children:
        return bot.answer_callback_query(ca.id, "❌ منقضی شد.")
    rid,sid = pending_children[mid], ca.from_user.id
    cur = conn.cursor()
    if ca.data.startswith("caccept_"):
        cur.execute("SELECT coin FROM users WHERE user_id=?", (rid,))
        if cur.fetchone()[0]<40:
            bot.edit_message_text("❌ سکه نیست!", ca.message.chat.id, mid)
            del pending_children[mid]; return
        cur.execute("UPDATE users SET child_of=?,coin=coin-40 WHERE user_id=?", (sid,rid))
        conn.commit()
        bot.edit_message_text("👶 پذیرفته شد!", ca.message.chat.id, mid)
        bot.send_message(ca.message.chat.id, f"🎉 @{get_username(rid)} فرزند @{get_username(sid)} شد!")
    else:
        bot.edit_message_text("❌ رد شد.", ca.message.chat.id, mid)
    del pending_children[mid]

@bot.message_handler(commands=['dchild'])
@blocked_guard
def cmd_dchild(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "❌ ریپلای کنید.")
    victim,uid = m.reply_to_message.from_user.id, m.from_user.id
    cur = conn.cursor()
    cur.execute("SELECT child_of FROM users WHERE user_id=?", (victim,))
    row = cur.fetchone()
    if not row or row[0]!=uid:
        return bot.reply_to(m, "❌ رابطه‌ای نیست.")
    cur.execute("UPDATE users SET child_of=NULL WHERE user_id=?", (victim,))
    conn.commit()
    bot.reply_to(m, f"🚼 @{get_username(victim)} حذف شد.")

# —————————————————————————————————————————————
# EMOJI SYSTEM
@bot.message_handler(commands=['emoji'])
@blocked_guard
def cmd_emoji(m):
    parts=m.text.strip().split(maxsplit=1)
    if len(parts)!=2:
        return bot.reply_to(m,"❌ /emoji 😎")
    em,uid=parts[1],m.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if cur.fetchone()[0]<50:
        return bot.reply_to(m,"❌ سکه کافی نیست!")
    cur.execute("UPDATE users SET custom_emoji=?,coin=coin-50 WHERE user_id=?", (em,uid))
    conn.commit()
    bot.reply_to(m,f"🎭 `{em}` ثبت شد! -50 سکه",parse_mode="Markdown")

@bot.message_handler(commands=['reemoji'])
@blocked_guard
def cmd_reemoji(m):
    uid=m.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT custom_emoji FROM users WHERE user_id=?", (uid,))
    if not cur.fetchone()[0]:
        return bot.reply_to(m,"❌ نداری!")
    cur.execute("UPDATE users SET custom_emoji=NULL WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m,"🎭 حذف شد.")

# —————————————————————————————————————————————
# GIVE: transfer coins
@bot.message_handler(commands=['give'])
@blocked_guard
def cmd_give(m):
    if not m.reply_to_message:
        return bot.reply_to(m,"❌ ریپلای کنید.")
    parts=m.text.strip().split()
    if len(parts)!=2 or not parts[1].isdigit():
        return bot.reply_to(m,"❌ /give مقدار")
    amt=int(parts[1])
    sid, rid = m.from_user.id, m.reply_to_message.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT coin FROM users WHERE user_id=?", (sid,))
    if cur.fetchone()[0]<amt:
        return bot.reply_to(m,"❌ سکه کافی نیست!")
    cur.execute("UPDATE users SET coin=coin-? WHERE user_id=?", (amt,sid))
    cur.execute("UPDATE users SET coin=coin+? WHERE user_id=?", (amt,rid))
    conn.commit()
    bot.reply_to(m,f"💸 @{get_username(sid)} → @{get_username(rid)} : {amt} سکه")

# —————————————————————————————————————————————
# CONTROL POINTS: +n / -n (score)  +n 🪙 / -n 🪙 (coin)
@bot.message_handler(func=lambda m: m.reply_to_message and bool(re.match(r'^(\+|\-)', m.text.strip())))
def control_points(m):
    uid=m.from_user.id
    if not(uid==OWNER_ID or is_admin(uid)):
        return
    target=m.reply_to_message.from_user.id
    text=m.text.strip()
    cur=conn.cursor()
    # score
    if m0:=re.match(r'^\+ (\d+)$', text):
        amt=int(m0.group(1))
        cur.execute("UPDATE users SET score=score+? WHERE user_id=?", (amt,target))
        conn.commit(); check_gold_tick(target)
        bot.reply_to(m,f"🎉 {amt} امتیاز به @{get_username(target)} افزوده شد!")
    elif m0:=re.match(r'^\- (\d+)$', text):
        amt=int(m0.group(1))
        cur.execute("UPDATE users SET score=score-? WHERE user_id=?", (amt,target))
        conn.commit()
        bot.reply_to(m,f"💔 {amt} امتیاز از @{get_username(target)} کسر شد!")
    # coin
    elif m0:=re.match(r'^\+ (\d+)\s+🪙$', text):
        amt=int(m0.group(1))
        cur.execute("UPDATE users SET coin=coin+? WHERE user_id=?", (amt,target))
        conn.commit()
        bot.reply_to(m,f"💰 {amt} سکه به @{get_username(target)} افزوده شد!")
    elif m0:=re.match(r'^\- (\d+)\s+🪙$', text):
        amt=int(m0.group(1))
        cur.execute("UPDATE users SET coin=coin-? WHERE user_id=?", (amt,target))
        conn.commit()
        bot.reply_to(m,f"💸 {amt} سکه از @{get_username(target)} کسر شد!")

# —————————————————————————————————————————————
# SET / UNSET ROLE: +mX / -mX
@bot.message_handler(func=lambda m: m.reply_to_message and re.match(r'^[\+\-]m\d+$', m.text.strip()))
def cmd_set_role(m):
    uid=m.from_user.id
    if not(uid==OWNER_ID or is_admin(uid)):
        return
    txt=m.text.strip()
    plus=txt.startswith("+")
    idx=txt[2:] if plus else txt[2:]
    key=f"m{idx}"
    new_role = ranks.get(key)
    if not new_role:
        return bot.reply_to(m,f"❌ کد مقام `{key}` معتبر نیست.")
    target=m.reply_to_message.from_user.id
    cur=conn.cursor()
    if plus:
        cur.execute("UPDATE users SET role=? WHERE user_id=?", (new_role,target))
        conn.commit()
        bot.reply_to(m,f"🏅 مقام @{get_username(target)} به «{new_role}» تغییر کرد!")
    else:
        default="ممبر عادی 🧍"
        cur.execute("UPDATE users SET role=? WHERE user_id=?", (default,target))
        conn.commit()
        bot.reply_to(m,f"🏅 مقام @{get_username(target)} به «{default}» برگشت داده شد!")

# —————————————————————————————————————————————
# SPELLS: /del & /mut
@bot.message_handler(commands=['del'])
@blocked_guard
def cmd_del(m):
    if not m.reply_to_message:
        return bot.reply_to(m,"❌ برای پاک‌سازی ریپلای کنید.")
    uid=m.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if cur.fetchone()[0]<20:
        return bot.reply_to(m,"❌ سکه کافی نیست!")
    try:
        bot.delete_message(m.chat.id, m.reply_to_message.message_id)
        cur.execute("UPDATE users SET coin=coin-20 WHERE user_id=?", (uid,))
        conn.commit()
        bot.reply_to(m,"✅ پیام پاک شد و ۲۰ سکه کسر گردید.")
    except Exception as e:
        bot.reply_to(m,f"❌ خطا در پاک‌سازی: {e}")

@bot.message_handler(commands=['mut'])
@blocked_guard
def cmd_mut(m):
    if not m.reply_to_message:
        return bot.reply_to(m,"❌ برای سکوت یخی ریپلای کنید.")
    uid=m.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if cur.fetchone()[0]<80:
        return bot.reply_to(m,"❌ سکه کافی نیست!")
    target=m.reply_to_message.from_user.id
    try:
        bot.restrict_chat_member(
            chat_id=m.chat.id,
            user_id=target,
            until_date=int(time.time())+60,
            can_send_messages=False
        )
        cur.execute("UPDATE users SET coin=coin-80 WHERE user_id=?", (uid,))
        conn.commit()
        bot.reply_to(m,"🧊 کاربر به مدت ۶۰ ثانیه سکوت شد و ۸۰ سکه کسر گردید.")
    except Exception as e:
        bot.reply_to(m,f"❌ خطا در سکوت یخی: {e}")

# —————————————————————————————————————————————
# ADMIN MANAGEMENT
@bot.message_handler(commands=['admin'])
def cmd_admin(m):
    if m.from_user.id!=OWNER_ID or not m.reply_to_message:
        return
    uid=m.reply_to_message.from_user.id
    add_user(uid, m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.username or "")
    cur=conn.cursor()
    cur.execute("UPDATE users SET is_admin=1 WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m,f"✅ @{get_username(uid)} مدیر شد.")

@bot.message_handler(commands=['dadmin'])
def cmd_dadmin(m):
    if m.from_user.id!=OWNER_ID or not m.reply_to_message:
        return
    uid=m.reply_to_message.from_user.id
    cur=conn.cursor()
    cur.execute("UPDATE users SET is_admin=0 WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m,f"❌ @{get_username(uid)} از مدیران حذف شد.")

@bot.message_handler(commands=['ddadmin'])
def cmd_ddadmin(m):
    if m.from_user.id!=OWNER_ID:
        return
    cur=conn.cursor()
    cur.execute("UPDATE users SET is_admin=0")
    conn.commit()
    bot.reply_to(m,"👢 همه مدیران حذف شدند.")

# —————————————————————————————————————————————
# SECT SYSTEM
@bot.message_handler(commands=['sectcreate'])
@blocked_guard
def cmd_sectcreate(m):
    parts=m.text.strip().split(maxsplit=1)
    if len(parts)!=2:
        return bot.reply_to(m,"❌ /sectcreate نام_فرقه")
    name,uid=parts[1],m.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT coin FROM users WHERE user_id=?", (uid,))
    if cur.fetchone()[0]<200:
        return bot.reply_to(m,"❌ سکه کافی نیست!")
    try:
        cur.execute("INSERT INTO sects(name,owner_id) VALUES(?,?)",(name,uid))
        cur.execute("UPDATE users SET sect=?,coin=coin-200 WHERE user_id=?", (name,uid))
        conn.commit()
        bot.reply_to(m,f"🌀 فرقهٔ `{name}` ساخته شد! -۲۰۰ سکه",parse_mode="Markdown")
    except sqlite3.IntegrityError:
        bot.reply_to(m,"❌ این فرقه قبلاً وجود دارد!")

@bot.message_handler(commands=['sectinvite'])
@blocked_guard
def cmd_sectinvite(m):
    if not m.reply_to_message:
        return bot.reply_to(m,"❌ برای دعوت ریپلای کنید.")
    inviter=m.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT sect FROM users WHERE user_id=?", (inviter,))
    row=cur.fetchone()
    if not row or not row[0]:
        return bot.reply_to(m,"❌ عضو هیچ فرقه‌ای نیستید!")
    sect=row[0]
    kb=types.InlineKeyboardMarkup()
    kb.add(
      types.InlineKeyboardButton("✅ می‌پذیرم", callback_data=f"saccept_{inviter}"),
      types.InlineKeyboardButton("❌ رد می‌کنم", callback_data=f"sreject_{inviter}")
    )
    uname=m.reply_to_message.from_user.username or m.reply_to_message.from_user.first_name
    sent=bot.send_message(m.chat.id,
      f"🌀 @{uname} به فرقهٔ `{sect}` دعوت شد. می‌پذیری؟",
      reply_markup=kb, parse_mode="Markdown")
    pending_sect_invites[sent.message_id]=inviter

@bot.callback_query_handler(lambda c: c.data.startswith(("saccept_","sreject_")))
def cb_sectinvite(ca):
    mid=ca.message.message_id
    if mid not in pending_sect_invites:
        return bot.answer_callback_query(ca.id,"❌ منقضی شد.")
    inv, res = pending_sect_invites[mid], ca.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT sect FROM users WHERE user_id=?", (inv,))
    sect=cur.fetchone()[0]
    if ca.data.startswith("saccept_"):
        cur.execute("UPDATE users SET sect=? WHERE user_id=?", (sect,res))
        conn.commit()
        bot.edit_message_text(f"✅ خوش آمدی به فرقهٔ `{sect}`!", ca.message.chat.id, mid, parse_mode="Markdown")
    else:
        bot.edit_message_text("❌ دعوت رد شد.", ca.message.chat.id, mid)
    del pending_sect_invites[mid]

@bot.message_handler(commands=['sectleave'])
@blocked_guard
def cmd_sectleave(m):
    uid=m.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT sect FROM users WHERE user_id=?", (uid,))
    if not cur.fetchone()[0]:
        return bot.reply_to(m,"❌ عضو هیچ فرقه‌ای نیستید!")
    cur.execute("UPDATE users SET sect=NULL WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m,"🌀 شما از فرقه خارج شدید.")

@bot.message_handler(commands=['sectdisband'])
@blocked_guard
def cmd_sectdisband(m):
    uid=m.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT name FROM sects WHERE owner_id=?", (uid,))
    row=cur.fetchone()
    if not row:
        return bot.reply_to(m,"❌ شما مالک هیچ فرقه‌ای نیستید!")
    name=row[0]
    cur.execute("DELETE FROM sects WHERE name=?", (name,))
    cur.execute("UPDATE users SET sect=NULL WHERE sect=?", (name,))
    conn.commit()
    bot.reply_to(m,f"🌀 فرقهٔ `{name}` منحل شد!", parse_mode="Markdown")

@bot.message_handler(commands=['dferghe'])
@blocked_guard
def cmd_dferghe(m):
    if not m.reply_to_message:
        return bot.reply_to(m,"❌ برای اخراج ریپلای کنید.")
    kicker, victim = m.from_user.id, m.reply_to_message.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT name FROM sects WHERE owner_id=?", (kicker,))
    row=cur.fetchone()
    if not row:
        return bot.reply_to(m,"❌ شما مالک هیچ فرقه‌ای نیستید!")
    name=row[0]
    cur.execute("SELECT sect FROM users WHERE user_id=?", (victim,))
    if not cur.fetchone()[0]==name:
        return bot.reply_to(m,"❌ فرد مورد نظر عضو فرقهٔ شما نیست!")
    cur.execute("UPDATE users SET sect=NULL WHERE user_id=?", (victim,))
    conn.commit()
    bot.reply_to(m,f"👢 @{get_username(victim)} از فرقهٔ `{name}` اخراج شد.", parse_mode="Markdown")

# —————————————————————————————————————————————
# TOP SECTS / MEE / BLOCK
@bot.message_handler(commands=['rank'])
@blocked_guard
def cmd_rank(m):
    if not sect_ranking_cache:
        return bot.reply_to(m,"⏳ رتبه‌بندی در حال آماده‌سازی است...")
    txt=f"📊 ۱۰ فرقه برتر تا {datetime.now().strftime('%H:%M')}:\n"
    for s,cnt in sect_ranking_cache:
        txt+=f"• `{s}` ({cnt} عضو)\n"
    bot.reply_to(m,txt,parse_mode="Markdown")

@bot.message_handler(commands=['mee'])
@blocked_guard
def cmd_mee(m):
    uid=m.from_user.id
    cur=conn.cursor()
    cur.execute("SELECT sect FROM users WHERE user_id=?", (uid,))
    row=cur.fetchone()
    if not row or not row[0]:
        return bot.reply_to(m,"❌ شما عضو هیچ فرقه‌ای نیستید!")
    sect=row[0]
    total=cur.execute("SELECT COUNT(*) FROM users WHERE sect=?", (sect,)).fetchone()[0]
    rank_pos=next((i+1 for i,(s,_) in enumerate(sect_ranking_cache) if s==sect),"–")
    bot.reply_to(m,
      f"🌀 اطلاعات فرقهٔ `{sect}`:\n• اعضا: {total}\n• رتبه: {rank_pos}\n",
      parse_mode="Markdown")

@bot.message_handler(commands=['block'])
def cmd_block(m):
    if not(m.from_user.id==OWNER_ID or is_admin(m.from_user.id)) or not m.reply_to_message:
        return
    uid=m.reply_to_message.from_user.id
    cur=conn.cursor()
    cur.execute("UPDATE users SET is_blocked=1 WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m,f"🔒 @{get_username(uid)} مسدود شد.")

@bot.message_handler(commands=['dblock'])
def cmd_dblock(m):
    if not(m.from_user.id==OWNER_ID or is_admin(m.from_user.id)) or not m.reply_to_message:
        return
    uid=m.reply_to_message.from_user.id
    cur=conn.cursor()
    cur.execute("UPDATE users SET is_blocked=0 WHERE user_id=?", (uid,))
    conn.commit()
    bot.reply_to(m,f"🔓 @{get_username(uid)} رفع مسدودیت شد.")

# —————————————————————————————————————————————
# SHOP / SPELLS
@bot.message_handler(commands=['shop'])
@blocked_guard
def cmd_shop(m):
    bot.reply_to(m,'''🎁 فروشگاه طلسم‌ها:
1️⃣ /del – ۲۰ سکه (پاک‌سازی پیام)
2️⃣ /mut – ۸۰ سکه (سکوت ۶۰ ثانیه)''')

# —————————————————————————————————————————————
# MESSAGE COUNTER & BONUS
@bot.message_handler(func=lambda m: True, content_types=['text'])
@blocked_guard
def on_any_message(m):
    uid=m.from_user.id
    add_user(uid, m.from_user.first_name, m.from_user.username or "")
    cur=conn.cursor()
    cur.execute("UPDATE users SET messages=messages+1 WHERE user_id=?", (uid,))
    conn.commit()
    cnt=cur.execute("SELECT messages FROM users WHERE user_id=?", (uid,)).fetchone()[0]
    if cnt%100==0:
        cur.execute("UPDATE users SET score=score+200,coin=coin+30 WHERE user_id=?", (uid,))
        conn.commit()
        bot.send_message(m.chat.id,
          f"🎉 @{m.from_user.username} شما {cnt} پیام فرستادید و 200 امتیاز + 30 سکه دریافت کردید!")

# —————————————————————————————————————————————
if __name__ == "__main__":
    bot.infinity_polling()
