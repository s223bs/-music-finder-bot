import os
import threading
import requests

from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

# Render uchun web server
web = Flask(__name__)

@web.route("/")
def home():
    return "🎵 Music Bot ishlayapti!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Salom!\n\n"
        "Qo‘shiq yoki ijrochi nomini yozing.\n\n"
        "Masalan:\n"
        "The Weeknd\n"
        "Blinding Lights"
    )


async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    await update.message.reply_text("🔎 Qidiryapman...")

    url = "https://itunes.apple.com/search"

    params = {
        "term": query,
        "entity": "song",
        "limit": 5
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if not results:
            await update.message.reply_text(
                "❌ Qo‘shiq topilmadi."
            )
            return

        for song in results:
            name = song.get("trackName", "Noma'lum")
            artist = song.get("artistName", "Noma'lum")
            preview = song.get("previewUrl")

            if preview:
                await update.message.reply_audio(
                    audio=preview,
                    title=name[:64],
                    performer=artist[:64],
                    caption=f"🎵 {name}\n🎤 {artist}\n\n30 soniyalik preview"
                )
                return

        await update.message.reply_text(
            "❌ Bu qo‘shiq uchun audio preview mavjud emas."
        )

    except Exception as e:
        print("Xatolik:", e)

        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi."
        )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN topilmadi!")

    # Web serverni alohida ishga tushirish
    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search_music
        )
    )

    print("🎵 Telegram bot ishga tushdi!")

    app.run_polling()


if __name__ == "__main__":
    main()
