import os
import requests
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ✅ المتغيرات البيئية
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ✅ الدالة: إرسال الرسالة لـ OpenRouter
def chat_with_openrouter(api_key, messages, model="openai/gpt-3.5-turbo"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://replit.com/@mj7addadcoder/shinjo-soul-gpt",  # يجب أن يكون رابط مشروع حقيقي
        "X-Title": "ShinjoSoulGPT"
    }
    data = {
        "model": model,
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ✅ تصنيف نبرة الرسالة
def detect_prompt_type(text: str) -> str:
    text = text.lower()
    if any(word in text for word in ["فضفض", "تعبان", "حزين", "ضايق", "قلقان"]):
        return "فضفضة"
    elif any(word in text for word in ["استشارة", "نصيحة", "مشكلة", "رأيك"]):
        return "استشارة"
    elif any(word in text for word in ["تحفيز", "حفزني", "محبط", "فشل"]):
        return "تحفيز"
    else:
        return "عام"

# ✅ أوامر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "👋 مرحباً بك في <b>Shinjo Soul GPT</b>!\n\n"
        "أنا رفيقك العاطفي الذكي، فضفض لي أو اطلب تحفيزًا أو استشارة.\n\n"
        "اكتب لي أي شيء الآن ❤️",
        reply_markup=ForceReply(selective=True)
    )

# ✅ /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 الأوامر المتاحة:\n"
        "/start – الترحيب\n"
        "/help – التعليمات\n"
        "فقط اكتب لي شعورك أو سؤالك وسأرد عليك تلقائيًا"
    )

# ✅ الرد على الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    prompt_type = detect_prompt_type(user_input)

    # موجه مخصص حسب نوع الرسالة
    system_prompt = {
        "فضفضة": "أنت رفيق عاطفي متفهم، استمع بلطف دون إصدار أحكام.",
        "استشارة": "أنت مستشار حكيم تحلل الموقف وتقدم رأيًا واضحًا.",
        "تحفيز": "أنت صديق داعم يشجع الآخرين بكلمات صادقة.",
        "عام": "كن مساعدًا ذكيًا لطيفًا يجيب باحترام."
    }.get(prompt_type, "كن مساعدًا لطيفًا.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    try:
        reply = chat_with_openrouter(OPENROUTER_API_KEY, messages)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء الاتصال بـ GPT:\n" + str(e))

# ✅ تشغيل البوت
def main():
    if not TELEGRAM_BOT_TOKEN or not OPENROUTER_API_KEY:
        raise ValueError("🚨 تأكد من وجود المتغيرات TELEGRAM_BOT_TOKEN و OPENROUTER_API_KEY")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 بوت Shinjo Soul GPT يعمل الآن!")
    app.run_polling()

if __name__ == "__main__":
    main()
