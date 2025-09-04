import { Telegraf, Markup } from 'telegraf'
import express from 'express'
import { RateLimiterMemory } from 'rate-limiter-flexible'

// ===== تنظیمات =====
const CONFIG = {
  token: '7583760165:AAHzGN-N7nyHgFoWt9oamd2tgO7pLkKFWFs', // توکن تو
  ownerId: 7341748124, // آیدی عددی تو
  useWebhook: false,
  port: 3000,
  domain: ''
}

// ===== پیام‌ها =====
const sig = (msg) => `${msg} :|`
const warm = (msg) => `${msg} ⚜️`
const lines = {
  welcome: (name) => sig(`نامت ثبت شد ${name}. آرام قدم بردار؛ اینجا قانون تنفس می‌کشد.`),
  softWarn: sig('کلمه‌هایت زیاد شد. سه گام عقب بنشین.'),
  muteEdict: sig('سکوت تا سپیده. وقتی بازگشتی، کمتر فریاد بزن.'),
  loyal: warm('اشاره کنی، انجام می‌شود. بقیه فقط می‌بینند.'),
  summonOwner: warm('حاضرم. فرمان بده.'),
  summonOther: sig('در سکوت بایست. من بیدارم.'),
  oath: sig('این‌جا قانون تنفس می‌کشد. می‌پذیری؟'),
  oathAccepted: sig('پذیرفته شد. قانون حافظ توست، نه زنجیرت.'),
  edictHeader: sig('حکم صادر شد.')
}

// ===== حالت‌ها =====
const MODES = ['warden', 'vow', 'edict']
const chatState = new Map()
function ensureChat(chatId) {
  if (!chatState.has(chatId)) chatState.set(chatId, { mode: 'warden' })
  return chatState.get(chatId)
}
function setMode(chatId, mode) {
  if (!MODES.includes(mode)) throw new Error('invalid mode')
  ensureChat(chatId).mode = mode
}
function getMode(chatId) {
  return ensureChat(chatId).mode
}

// ===== ضداسپم =====
const perUserLimiter = new RateLimiterMemory({ points: 6, duration: 8 })
const perChatLimiter = new RateLimiterMemory({ points: 60, duration: 10 })
async function rateGuard(ctx, next) {
  const uid = ctx.from?.id
  const cid = ctx.chat?.id
  if (!uid || !cid) return next()
  try {
    await Promise.all([
      perUserLimiter.consume(String(uid), 1),
      perChatLimiter.consume(String(cid), 1)
    ])
    return next()
  } catch {
    if (ctx.message) {
      try { await ctx.reply(sig('آرام‌تر. نفس بگیر.')) } catch {}
    }
    try {
      const meAdmin = await ctx.getChatMember((await ctx.getMe()).id)
      if (meAdmin?.can_delete_messages && ctx.message?.message_id) {
        await ctx.deleteMessage(ctx.message.message_id)
      }
    } catch {}
  }
}

// ===== ربات =====
const bot = new Telegraf(CONFIG.token, { handlerTimeout: 9000 })
bot.use(rateGuard)

bot.start(async (ctx) => {
  const name = ctx.from?.first_name || 'مسافر'
  await ctx.reply(lines.welcome(name))
})

bot.command('summon', async (ctx) => {
  const isOwner = ctx.from?.id === CONFIG.ownerId
  await ctx.reply(isOwner ? lines.summonOwner : lines.summonOther)
})

bot.command('oath', async (ctx) => {
  await ctx.reply(
    lines.oath,
    Markup.inlineKeyboard([Markup.button.callback('می‌پذیرم', 'oath_accept')])
  )
})
bot.action('oath_accept', async (ctx) => {
  await ctx.answerCbQuery('پذیرفته شد')
  await ctx.editMessageText(lines.oathAccepted)
})

bot.command('mode', async (ctx) => {
  const mode = ctx.message.text.split(' ')[1]
  if (!mode) {
    await ctx.reply(
      sig(`حالت جاری: ${getMode(ctx.chat.id)}. یکی را انتخاب کن:`),
      Markup.inlineKeyboard(
        MODES.map(m => Markup.button.callback(m.toUpperCase(), `mode_${m}`)),
        { columns: 3 }
      )
    )
    return
  }
  try {
    setMode(ctx.chat.id, mode)
    await ctx.reply(sig(`حالت به ${mode.toUpperCase()} تغییر کرد.`))
  } catch {
    await ctx.reply(sig(`حالت نامعتبر. گزینه‌ها: ${MODES.join(', ')}`))
  }
})
MODES.forEach(m =>
  bot.action(`mode_${m}`, async (ctx) => {
    setMode(ctx.chat.id, m)
    await ctx.editMessageText(sig(`حالت به ${m.toUpperCase()} تغییر کرد.`))
  })
)

bot.command('edict', async (ctx) => {
  const mode = getMode(ctx.chat.id)
  if (mode !== 'edict') return ctx.reply(sig('در این حالت، حکم خاموش است.'))
  const text = ctx.message.text.replace('/edict', '').trim() || 'بدون شرح.'
  await ctx.reply(`${lines.edictHeader}\n— ${text}`)
})

bot.command('veil', async (ctx) => {
  const replyTo = ctx.message?.reply_to_message
  if (!replyTo) return ctx.reply(sig('روی پیام هدف ریپلای کن و /veil بزن.'))
  const targetId = replyTo.from?.id
  try {
    await ctx.restrictChatMember(targetId, { permissions: { can_send_messages: false } })
    await ctx.reply(lines.muteEdict)
  } catch {
    await ctx.reply(sig('اجازهٔ کافی برای سکوت ندارم.'))
  }
})

bot.command('status', async (ctx) => {
  await ctx.reply(sig(`mode=${getMode(ctx.chat.id)}`))
})

bot.on('message', async (ctx, next) => {
  if (ctx.from?.id === CONFIG.ownerId && Math.random() < 0.02) {
    try { await ctx.reply(warm('دیدم. به چشم.')) } catch {}
  }
  return next()
})

// ===== اجرا =====
async function main() {
  if (CONFIG.useWebhook) {
    const app = express()
    app.use(await bot.createWebhook({ domain: CONFIG.domain }))
    app.listen(CONFIG.port, () => {
      console.log(`[legend-bot] webhook on ${CONFIG.port}`)
    })
  } else {
    await bot.launch()
    console.log('[legend-bot] polling started')
  }
}
process.once('SIGINT', () => bot.stop('SIGINT'))
process.once('SIGTERM', () => bot.stop('SIGTERM'))
main()
