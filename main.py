import os
import requests
from telegram import Update, ForceReply, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# قراءة المتغيرات من البيئة (Replit Secrets أو .env)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# دالة الاتصال بـ OpenRouter
def chat_with_openrouter(api_key, messages, model="openrouter/openchat"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://replit.com/@mj7addadcoder/shinjo-soul-gpt",  # مهم جدًا لتفادي 401
        "X-Title": "ShinjoSoulBot"
    }
    data = {
        "model": model,
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# تحليل نوع الرسالة
def detect_prompt_type(text: str) -> str:
    text = text.lower()
    if any(word in text for word in ["فضفض", "تعبان", "حزين", "مخنوق"]):
        return "فضفضة"
    elif any(word in text for word in ["استشارة", "رأيك", "مشورة"]):
        return "استشارة"
    elif any(word in text for word in ["حفزني", "تحفيز", "يأس"]):
        return "تحفيز"
    else:
        return "عام"

# أوامر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"مرحبًا بك، أنا <b>Shinjo Soul GPT</b> – رفيقك العاطفي.\n\nأرسل لي مشاعرك وسأحاول مساعدتك 💜",
        reply_markup=ForceReply(selective=True)
    )

# /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💡 شينچو سول GPT – بوت دعم نفسي عاطفي مبني على OpenRouter. الإصدار المجاني ✨")

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 الأوامر المتاحة:\n"
        "/start – بداية جديدة\n"
        "/mood – تحليل مشاعرك\n"
        "/soul – رسالة تحفيزية\n"
        "/about – عن البوت\n"
        "/help – المساعدة"
    )

# /mood
async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 أرسل لي شعورك الحالي وسأحاول مساعدتك باستخدام GPT...")

# /soul
async def soul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌟 اكتب لي كلمة تحفيزية أو شعورك وسأرسل لك ردًا خاصًا 💜")

# ردود عامة
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    prompt_type = detect_prompt_type(user_input)

    system_prompt = {
        "فضفضة": "أنت رفيق عاطفي متفهم، لا تصدر أحكام، فقط استمع ورد بلطف.",
        "استشارة": "أنت مستشار حكيم تحلل المواقف وتقدم رأيًا عقلانيًا.",
        "تحفيز": "أنت صديق داعم يشعل الحماس بكلمات صادقة.",
        "عام": "كن رفيقًا ذكيًا يتفاعل بلطف مع أي رسالة."
    }.get(prompt_type, "عام")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    try:
        reply = chat_with_openrouter(OPENROUTER_API_KEY, messages)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("حدث خطأ أثناء الاتصال بـ GPT: " + str(e))

# تشغيل البوت
def main():
    if not TELEGRAM_BOT_TOKEN or not OPENROUTER_API_KEY:
        raise ValueError("❌ تأكد من إضافة TELEGRAM_BOT_TOKEN و OPENROUTER_API_KEY في البيئة")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # تسجيل الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(CommandHandler("soul", soul))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
