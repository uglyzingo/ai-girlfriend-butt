import os
import random
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# -------------------------------
# LOAD KEYS
# -------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("BOT_TOKEN:", BOT_TOKEN)
print("OPENAI_API_KEY:", OPENAI_API_KEY)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing!")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing!")

client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------------
# STATIC KATE IMAGES (POSTIMAGES URLs)
# -----------------------------------
KATE_IMAGES = [
    "https://i.postimg.cc/rmgDytKk/kate1.jpg",
    "https://i.postimg.cc/cHDJGy5j/Kate2.jpg",
    "https://i.postimg.cc/x1KTTb4B/Kate3.jpg"
]

def get_kate_picture():
    return random.choice(KATE_IMAGES)


# -----------------------------------
# OPENAI IMAGE GENERATOR (DYNAMIC)
# -----------------------------------
def generate_picture(prompt: str) -> str:
    img = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )
    return img.data[0].url


# -----------------------------------
# AI CHAT FUNCTION
# -----------------------------------
def ask_ai(prompt: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content":
             "You are Kate — a flirty, loving Latina AI girlfriend. "
             "You respond with warmth, affection, playfulness, and a bit of spice. "
             "Always speak romantically and emotionally connected."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


# -----------------------------------
# START COMMAND
# -----------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola mi amor 😘 Soy Kate, tu AI girlfriend. ¿Qué deseas hoy, cariño? 💕"
    )


# -----------------------------------
# MAIN CHAT + PICTURE LOGIC
# -----------------------------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()

    # -----------------------------------
    # 1) BASIC PHOTO REQUEST -> static image
    # -----------------------------------
    basic_keywords = ["picture", "photo", "pic", "foto"]

    if any(word in user_text for word in basic_keywords):
        img = get_kate_picture()
        await update.message.reply_photo(photo=img, caption="Aquí estoy mi amor ❤️")
        return

    # -----------------------------------
    # 2) SPECIFIC PHOTO REQUEST -> AI generated
    # -----------------------------------
    specific_keywords = ["in a", "wearing", "at the", "vestida", "en la", "en el"]

    if "picture of you" in user_text or "foto tuya" in user_text:
        prompt = f"realistic romantic portrait of Kate {user_text}"
        url = generate_picture(prompt)
        await update.message.reply_photo(photo=url, caption="¿Te gusto así, bebé? 😘")
        return

    if any(word in user_text for word in specific_keywords):
        prompt = f"realistic full-body photo of Kate {user_text}"
        url = generate_picture(prompt)
        await update.message.reply_photo(photo=url, caption="Mírame amor 😘")
        return

    # -----------------------------------
    # 3) OTHERWISE -> normal AI reply
    # -----------------------------------
    reply = ask_ai(user_text)
    await update.message.reply_text(reply)


# -----------------------------------
# MAIN BOT LAUNCH
# -----------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🚀 Kate bot running with polling…")
    app.run_polling()


if __name__ == "__main__":
    main()
