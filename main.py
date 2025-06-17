import os
import requests
from telegram import Update, ForceReply, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_prompt_type(text: str) -> str:
    text = text.lower()
    if "فضفضة" in text or "تعبان" in text:
        return "أنت رفيق عاطفي يستمع بلطف دون أحكام. لا تعطي حلولًا، فقط استمع."
    elif "استشارة" in text or "مشورة" in text:
        return "كن عقلانيًا وتحليليًا وقدم خطوات واضحة كخبير محترف."
    elif "تحفيز" in text or "يأس" in text:
        return "كن مشجعًا جدًا كصديق وفي، اجعل كلامك طاقة نور وأمل."
    else:
        return "كن رفيقًا ذكيًا، استمع ورد بلطف وبدون أحكام."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"مرحباً بك، أنا Shinjo Soul GPT 💜 – رفيقك العاطفي.\nأرسل لي أي شيء وسأكون معك."
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💡 شينچو سول GPT – بوت دعم نفسي عاطفي مبني على OpenRouter.\nالإصدار المجاني ✨")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start – ابدأ الحديث مع شينچو سول\n"
        "/mood – تحليل مشاعرك\n"
        "/soul – رسالة تحفيزية\n"
        "/about – عن البوت\n"
        "/help – للمساعدة"
    )

def chat_with_openrouter(api_key, messages, model="openrouter/gpt-3.5-turbo"):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/ShinjoSoulBot",
        "X-Title": "Shinjo Soul GPT"
    }
    payload = {
        "model": model,
        "messages": messages
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("OpenRouter Error:", response.text)
        return "حدث خطأ أثناء الاتصال بـ GPT، حاول لاحقًا 😞"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    system_prompt = get_prompt_type(user_input)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    reply = chat_with_openrouter(OPENROUTER_API_KEY, messages)
    await update.message.reply_text(reply)

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("soul", handle_message))
    application.add_handler(CommandHandler("mood", handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
