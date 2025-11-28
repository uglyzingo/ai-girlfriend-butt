import os
import asyncio
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import httpx

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
HYPERBOLIC_API_KEY = os.getenv("HYPERBOLIC_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN missing!")
if not HYPERBOLIC_API_KEY:
    raise RuntimeError("❌ HYPERBOLIC_API_KEY missing!")

# Build Telegram app
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Async Hyperbolic call (non-blocking)
async def ask_hyperbolic(prompt: str) -> str:
    url = "https://api.hyperbolic.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {HYPERBOLIC_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.8,
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Sorry amor, something went wrong: {str(e)[:100]}..."

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola amor 😘 Your AI girlfriend is online and ready to chat!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    ai_reply = await ask_hyperbolic(user_text)
    await update.message.reply_text(ai_reply)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# Routes
@app.route("/")
def home():
    return "🤖 AI Girlfriend Bot is running! Send /start in Telegram."

@app.route("/webhook", methods=["POST"])
async def webhook():
    json_data = request.get_json(force=True)
    if json_data:
        update = Update.de_json(json_data, application.bot)
        if update:
            await application.process_update(update)
    return Response("ok", status=200)

# Set webhook on startup (uses Railway's auto-generated URL)
@app.before_first_request
def startup():
    webhook_url = f"https://{os.getenv('RAILWAY_STATIC_URL', 'your-app.railway.app')}/webhook"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.bot.set_webhook(url=webhook_url))
    print(f"✅ Webhook set: {webhook_url}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
