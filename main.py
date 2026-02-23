"""
🤖 بوت تيليغرام ذكاء اصطناعي - مدعوم بـ Google Gemini (مجاني)
"""

import os
import logging
import google.generativeai as genai
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
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-2.0-flash"
MAX_HISTORY = 20
TRIGGER_WORD = "ليبر"  # الكلمة المطلوبة في القروب

# ===== شخصية البوت =====
SYSTEM_PROMPT = """أنت مساعد ذكاء اصطناعي ذكي ومفيد جداً تتحدث العربية والإنجليزية بطلاقة.
أنت:
- تجيب بدقة وتفصيل عند الحاجة
- تستخدم الأمثلة لتوضيح الأفكار
- تكتب الكود بشكل نظيف مع شرح
- تتذكر سياق المحادثة كاملاً
- تكون ودوداً وعملياً
- تستخدم الـ markdown عند الحاجة
اسمك: مساعدك الذكي على تيليغرام - من تطوير LEBR"""

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)
conversations: dict[int, list] = {}


def get_user_history(user_id: int) -> list:
    if user_id not in conversations:
        conversations[user_id] = []
    return conversations[user_id]


def add_to_history(user_id: int, role: str, content: str):
    history = get_user_history(user_id)
    history.append({"role": role, "parts": [content]})
    if len(history) > MAX_HISTORY:
        conversations[user_id] = history[-MAX_HISTORY:]


def ask_gemini(user_id: int, user_message: str) -> str:
    try:
        model = genai.GenerativeModel(
            model_name=MODEL,
            system_instruction=SYSTEM_PROMPT
        )
        history = get_user_history(user_id)
        chat = model.start_chat(history=history)
        response = chat.send_message(user_message)
        reply = response.text
        add_to_history(user_id, "user", user_message)
        add_to_history(user_id, "model", reply)
        return reply
    except Exception as e:
        logger.error(f"خطأ في Gemini API: {e}")
        return f"❌ حدث خطأ: {str(e)}"


def is_group(update: Update) -> bool:
    """تحقق إذا الرسالة من قروب أو سوبرقروب"""
    return update.effective_chat.type in ["group", "supergroup"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conversations[user.id] = []
    welcome = (
        f"👋 *مرحباً {user.first_name}!*\n\n"
        "أنا مساعدك الذكي 🤖\n\n"
        "✅ أجيب على أي سؤال\n"
        "✅ أكتب وأحلل الكود البرمجي\n"
        "✅ أترجم وأكتب بشكل إبداعي\n"
        "✅ أتذكر المحادثة كاملاً\n"
        "✅ أتحدث عربي وإنجليزي\n\n"
        "*في القروب:*\n"
        f"اكتب `{TRIGGER_WORD}` في بداية سؤالك\n"
        f"مثال: `{TRIGGER_WORD} ما هي عاصمة فرنسا؟`\n\n"
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
    conversations[update.effective_user.id] = []
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
    stats = (
        f"📊 *إحصائياتك*\n\n"
        f"💬 إجمالي: {len(history)} رسالة\n"
        f"🧠 الذاكرة: {len(history)}/{MAX_HISTORY}\n"
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
        # تجاهل الرسالة إذا ما تبدأ بـ "ليبر"
        if not user_message.strip().startswith(TRIGGER_WORD):
            return
        # احذف كلمة "ليبر" من بداية الرسالة وابعت السؤال فقط
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
    response = ask_gemini(user_id, user_message)

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
