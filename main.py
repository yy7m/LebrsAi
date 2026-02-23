"""
🤖 بوت تيليغرام ذكاء اصطناعي - مدعوم بـ Groq (مجاني وسريع)
"""

import os
import logging
from groq import Groq
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ChatAction, ParseMode

# ===== الإعدادات =====
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
MODEL = "llama-3.3-70b-versatile"
MAX_HISTORY = 20
TRIGGER_WORD = "ليبر"

# ===== شخصية البوت =====
SYSTEM_PROMPT = """أنت مساعد ذكاء اصطناعي ذكي ومفيد جداً تتحدث العربية والإنجليزية بطلاقة.
أنت:
- تجيب بدقة وتفصيل عند الحاجة
- تستخدم الأمثلة لتوضيح الأفكار
- تكتب الكود بشكل نظيف مع شرح
- تتذكر سياق المحادثة كاملاً
- تكون ودوداً وعملياً
اسمك: مساعدك الذكي على تيليغرام - من تطوير LEBR"""

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)
conversations: dict[int, list] = {}


def get_user_history(user_id: int) -> list:
    if user_id not in conversations:
        conversations[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return conversations[user_id]


def add_to_history(user_id: int, role: str, content: str):
    history = get_user_history(user_id)
    history.append({"role": role, "content": content})
    # احتفظ بـ system message + آخر MAX_HISTORY رسالة
    if len(history) > MAX_HISTORY + 1:
        conversations[user_id] = [history[0]] + history[-(MAX_HISTORY):]


def ask_groq(user_id: int, user_message: str) -> str:
    add_to_history(user_id, "user", user_message)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=get_user_history(user_id),
            max_tokens=4096,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        add_to_history(user_id, "assistant", reply)
        return reply
    except Exception as e:
        logger.error(f"خطأ في Groq API: {e}")
        # احذف الرسالة الأخيرة عند الخطأ
        conversations[user_id].pop()
        return f"❌ حدث خطأ: {str(e)}"


def is_group(update: Update) -> bool:
    return update.effective_chat.type in ["group", "supergroup"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conversations[user.id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    welcome = (
        f"👋 *مرحباً {user.first_name}!*\n\n"
        "أنا مساعدك الذكي 🤖\n\n"
        "✅ أجيب على أي سؤال\n"
        "✅ أكتب وأحلل الكود البرمجي\n"
        "✅ أترجم وأكتب بشكل إبداعي\n"
        "✅ أتذكر المحادثة كاملاً\n"
        "✅ أتحدث عربي وإنجليزي\n\n"
        "*في القروب:*\n"
        f"ابدأ رسالتك بـ `{TRIGGER_WORD}` ثم سؤالك\n"
        f"مثال: `{TRIGGER_WORD} ما هي عاصمة العراق؟`\n\n"
        "*الأوامر:*\n"
        "/new - محادثة جديدة\n"
        "/stats - إحصائياتك\n"
        "/help - المساعدة\n\n"
        "ابدأ بكتابة سؤالك الآن! 💬\n\n"
        "━━━━━━━━━━━━━━━\n"
        "🛠️ _تم تطوير هذا البوت بواسطة LEBR_"
    )
    await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN)


async def new_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversations[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await update.message.reply_text(
        "🔄 *تم مسح المحادثة السابقة!*\nابدأ محادثة جديدة الآن 💬",
        parse_mode=ParseMode.MARKDOWN
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *دليل الاستخدام*\n\n"
        "*في الخاص:*\n"
        "فقط اكتب رسالتك وسأرد فوراً!\n\n"
        "*في القروب:*\n"
        f"ابدأ رسالتك بـ `{TRIGGER_WORD}` ثم سؤالك\n"
        f"مثال: `{TRIGGER_WORD} اشرح الذكاء الاصطناعي`\n\n"
        "*أمثلة:*\n"
        "🔷 `اكتب كود Python لقراءة CSV`\n"
        "🔷 `اشرح كيف يعمل ChatGPT`\n"
        "🔷 `ترجم هذا النص: [النص]`\n\n"
        "*الأوامر:*\n"
        "/new - محادثة جديدة\n"
        "/stats - إحصائياتك"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    history = get_user_history(user_id)
    msgs = len([m for m in history if m["role"] != "system"])
    stats = (
        f"📊 *إحصائياتك*\n\n"
        f"💬 إجمالي: {msgs} رسالة\n"
        f"🧠 الذاكرة: {msgs}/{MAX_HISTORY}\n"
        f"🤖 الموديل: `{MODEL}`"
    )
    await update.message.reply_text(stats, parse_mode=ParseMode.MARKDOWN)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    if not user_message:
        return

    # ===== منطق القروب =====
    if is_group(update):
        if not user_message.strip().startswith(TRIGGER_WORD):
            return
        user_message = user_message.strip()[len(TRIGGER_WORD):].strip()
        if not user_message:
            await update.message.reply_text(
                f"❓ اكتب سؤالك بعد كلمة *{TRIGGER_WORD}*\n"
                f"مثال: `{TRIGGER_WORD} ما هي عاصمة العراق؟`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    logger.info(f"رسالة من {user_id}: {user_message[:50]}...")
    response = ask_groq(user_id, user_message)

    if len(response) <= 4096:
        try:
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await update.message.reply_text(response)
    else:
        parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for part in parts:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=part,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=part
                )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"خطأ: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "❌ حدث خطأ. حاول مرة أخرى أو استخدم /new"
        )


def main():
    print("🚀 جاري تشغيل البوت...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_conversation))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    print("✅ البوت يعمل الآن!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
    
