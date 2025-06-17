import os
import requests
from telegram import Update, ForceReply, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# 🔐 مفاتيح API من المتغيرات البيئية
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 🧠 الدالة الأساسية للتواصل مع OpenRouter
def chat_with_openrouter(api_key, messages, model="openrouter/gpt-3.5-turbo"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        return reply
    except requests.exceptions.RequestException as e:
        return f"حدث خطأ أثناء الاتصال بـ GPT: {e}"

# 🎯 تحليل نوع الرسالة لاختيار النبرة المناسبة
def get_prompt_type(text: str) -> str:
    text = text.lower()
    if any(word in text for word in ["فضفض", "تعبان", "زعلان", "ضايق"]):
        return "أنت صديق حنون، تستمع فقط دون أحكام."
    elif any(word in text for word in ["رأيك", "استشارة", "شو رأيك"]):
        return "كن عقلانياً، وقدّم رأيًا منظمًا ومفيدًا."
    elif any(word in text for word in ["حفزني", "طاقة", "تشجيع", "يأس"]):
        return "أنت محفّز وداعم، تشعل الأمل في النفس."
    else:
        return "أنت مساعد ذكي وداعم، لطيف وحيادي."

# 🟢 أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = f"مرحباً {user.first_name}! 💜\nأنا شينچو سول GPT – رفيقك العاطفي. أرسل لي أي شيء 🧠"
    await update.message.reply_text(message)

# 🟣 أوامر وصفية
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💡 شينچو سول GPT – بوت دعم نفسي عاطفي مبني على OpenRouter. الإصدار المجاني ✨")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("بداية جديدة: /start\nتحليل مشاعرك: /mood\nرسالة تحفيزية: /soul\nعن البوت: /about\nللمساعدة: /help")

async def soul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "أعطني رسالة تحفيزية قصيرة بلغة عاطفية وداعمة لأحد يشعر بالإرهاق واليأس."
    messages = [{"role": "user", "content": prompt}]
    reply = chat_with_openrouter(OPENROUTER_API_KEY, messages)
    await update.message.reply_text(reply)

async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 أرسل لي شعورك الحالي وسأحلله لك باستخدام GPT...")

# 🧠 الرسائل العامة
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    prompt_type = get_prompt_type(user_text)
    messages = [
        {"role": "system", "content": prompt_type},
        {"role": "user", "content": user_text}
    ]
    reply = chat_with_openrouter(OPENROUTER_API_KEY, messages)
    await update.message.reply_text(reply)

# 🚀 تشغيل البوت
def main():
    if not TELEGRAM_BOT_TOKEN or not OPENROUTER_API_KEY:
        raise ValueError("❌ تأكد من وجود TELEGRAM_BOT_TOKEN و OPENROUTER_API_KEY.")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("soul", soul))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
