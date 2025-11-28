import os
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import httpx

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
HYPERBOLIC_API_KEY = os.getenv("HYPERBOLIC_API_KEY")

application = ApplicationBuilder().token(BOT_TOKEN).build()

async def ask_hyperbolic(prompt: str) -> str:
    url = "https://api.hyperbolic.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HYPERBOLIC_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.8,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error amor: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola amor, your AI girlfriend is here")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await ask_hyperbolic(update.message.text)
    await update.message.reply_text(reply)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

@app.route("/")
def home():
    return "AI girlfriend bot running!"

@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    if update:
        await application.process_update(update)
    return Response("ok", status=200)

# Set webhook on first request
@app.before_first_request
def set_webhook():
    import asyncio
    url = f"https://{os.getenv('RAILWAY_STATIC_URL')}/webhook"
    asyncio.run(application.bot.set_webhook(url=url))
    print(f"Webhook set to {url}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
