import os
import requests
from telegram import Update, ForceReply, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def chat_with_openrouter(api_key, messages, model="openrouter/gpt-3.5-turbo"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {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}",
        "Content-Type": "application/json"
    }
    payload = {"model": model, "messages": messages}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return "حدث خطأ أثناء الاتصال بـ GPT: " + str(e)

def get_prompt_type(text: str) -> str:
    text = text.lower()
    if any(w in text for w in ["فضفضة", "أبوح", "تعبان", "قلق", "وحداني", "ضيق"]):
        return "أنت رفيق عاطفي يستمع دون حكم. كن حنونًا وداعمًا."
    elif any(w in text for w in ["استشارة", "رأيك", "مشورة", "هل أبدأ"]):
        return "أنت مستشار حكيم يعطي رأيًا عقلانيًا ومنطقيًا."
    elif any(w in text for w in ["تحفيز", "يأس", "فشل", "أحبط"]):
        return "كن محفزًا وصديقًا يشعل الأمل."
    else:
        return "كن مساعدًا ذكيًا، ورد بلطف دون أحكام."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"مرحباً {user.first_name}! 💜\n\nأنا شينچو سول – رفيقك العاطفي. أرسل لي مشاعرك، فضفض لي، وخليني أساعدك.\nاكتب أي شيء الآن..."
    )

async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 أرسل لي شعورك الحالي وسأحلله لك باستخدام GPT...")

async def soul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = chat_with_openrouter(OPENROUTER_API_KEY, [
        {"role": "system", "content": "أرسل جملة تحفيزية قصيرة تشعل الأمل."},
        {"role": "user", "content": "أعطني رسالة تحفيزية الآن"}
    ])
    await update.message.reply_text(msg)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💡 شينچو سول GPT – بوت دعم نفسي عاطفي مبني على OpenRouter. الإصدار المجاني ✨")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start – بداية جديدة\n/mood – تحليل مشاعري\n/soul – رسالة تحفيزية\n/about – عن البوت\n/help – المساعدة")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    prompt = get_prompt_type(text)
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": text}]
    reply = chat_with_openrouter(OPENROUTER_API_KEY, messages)
    await update.message.reply_text(reply)

async def set_commands(app: Application):
    commands = [
        BotCommand("start", "ابدأ الحديث مع شينچو سول"),
        BotCommand("mood", "تحليل مشاعرك"),
        BotCommand("soul", "رسالة تحفيزية"),
        BotCommand("about", "عن البوت"),
        BotCommand("help", "المساعدة")
    ]
    await app.bot.set_my_commands(commands)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(CommandHandler("soul", soul))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.post_init = lambda _: set_commands(app)
    app.run_polling()

if __name__ == "__main__":
    main()
