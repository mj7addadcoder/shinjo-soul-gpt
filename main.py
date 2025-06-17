import os
import requests
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def chat_with_openrouter(api_key, messages, model="openai/gpt-3.5-turbo"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "ShinjoSoulGPT",  # عنوان مخصص
        "HTTP-Referer": "https://replit.com/@mj7addadcoder/shinjo-soul-gpt"  # رابط مشروعك الحقيقي
    }
    data = {
        "model": model,
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)

    # لو الخطأ موجود، اطبعه بوضوح
    if not response.ok:
        raise Exception(f"{response.status_code} – {response.text}")

    return response.json()["choices"][0]["message"]["content"]

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا بك، أنا Shinjo Soul – رفيقك العاطفي. أرسل لي أي شعور أو سؤال ❤️‍🔥")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 الأوامر المتاحة:\n/start – البداية\n/help – المساعدة\n/mood – تحليل مشاعرك\n/soul – رسالة تحفيزية")

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
        await update.message.reply_text("❌ حدث خطأ أثناء الاتصال بـ GPT:\n" + str(e))

def main():
    if not TELEGRAM_BOT_TOKEN or not OPENROUTER_API_KEY:
        raise Exception("❌ تأكد من وجود المتغيرات البيئية")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
